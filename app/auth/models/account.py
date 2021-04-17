from typing import Union, Optional, List
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.db import TortoiseBaseUserModel
from tortoise import fields, models
from tortoise.query_utils import Prefetch
from limeutils import modstr, valid_str_only
from tortoise.manager import Manager

from app import ic, cache
from app.settings import settings as s
from app.cache import red, makesafe
from app.auth.models.core import DTMixin, Option, SharedMixin
from app.auth.models.manager import ActiveManager



tokenonly = OAuth2PasswordBearer(tokenUrl='token')

class UserMod(DTMixin, TortoiseBaseUserModel):
    username = fields.CharField(max_length=50, null=True)
    first_name = fields.CharField(max_length=191, default='')
    middle_name = fields.CharField(max_length=191, default='')
    last_name = fields.CharField(max_length=191, default='')
    
    civil = fields.CharField(max_length=20, default='')
    bday = fields.DateField(null=True)
    mobile = fields.CharField(max_length=50, default='')
    telephone = fields.CharField(max_length=50, default='')
    avatar = fields.CharField(max_length=191, default='')
    status = fields.CharField(max_length=20, default='')
    bio = fields.CharField(max_length=191, default='')
    address1 = fields.CharField(max_length=191, default='')
    address2 = fields.CharField(max_length=191, default='')
    country = fields.CharField(max_length=2, default='')
    zipcode = fields.CharField(max_length=20, default='')
    timezone = fields.CharField(max_length=10, default='+00:00')
    website = fields.CharField(max_length=20, default='')
    
    last_login = fields.DatetimeField(null=True)
    
    groups = fields.ManyToManyField('models.Group', related_name='group_users',
                                    through='auth_user_groups', backward_key='user_id')
    permissions = fields.ManyToManyField('models.Permission', related_name='permission_users',
                                         through='auth_user_permissions', backward_key='user_id')
    
    full = Manager()
    
    class Meta:
        table = 'auth_user'
        manager = ActiveManager()
    
    def __str__(self):
        return modstr(self, 'id')
    
    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    @property
    async def display_name(self):
        if self.username:
            return self.username
        elif self.fullname:
            return self.fullname.split()[0]
        else:
            return self.email.split('@')[0]
    
    async def to_dict(self, exclude: Optional[List[str]] = None, prefetch=False) -> dict:
        """
        Converts a UserMod instance into UserModComplete. Included fields are based on UserDB +
        groups, options, and permissions.
        :param exclude:     Fields not to explicitly include
        :param prefetch:    Query used prefetch_related to save on db hits
        :return:            UserDBComplete
        """
        d = {}
        exclude = ['created_at', 'deleted_at', 'updated_at'] if exclude is None else exclude
        for field in self._meta.db_fields:
            if hasattr(self, field) and field not in exclude:
                d[field] = getattr(self, field)
                if field == 'id':
                    d[field] = str(d[field])

        # UPGRADE: Add the tax to list of keys once in use
        if hasattr(self, 'groups'):
            if prefetch:
                d['groups'] = [i.name for i in self.groups]
            else:
                d['groups'] = await self.groups.all().values_list('name', flat=True)
        if hasattr(self, 'options'):
            if prefetch:
                d['options'] = {i.name: i.value for i in self.options}
            else:
                d['options'] = {
                    i.name: i.value for i in await self.options.all().only('id', 'name', 'value', 'is_active') if i.is_active
                }
        # if hasattr(self, 'permissions'):
        #     d['permissions'] = [i.code for i in await self.permissions.all().only('id', 'code')]
        # ic(d)
        return d

    async def get_and_cache(self, id, model=False):
        """
        Get a user's cachable data and cache it for future use. Replaces data if exists.
        Similar to the dependency current_user.
        :param id:      User id as str
        :param model:   Also return the UserMod instance
        :return:        DOESN'T NEED cache.restoreuser() since data is from the db not redis.
                        The id key in the hash is already formatted to a str from UUID.
        """
        from app.auth import userdb
        
        query = self.get_or_none(pk=id) \
            .prefetch_related(
                Prefetch('groups', queryset=Group.filter(deleted_at=None)
                         .only('id', 'name')),
                Prefetch('options', queryset=Option.filter(is_active=True)
                         .only('user_id', 'name', 'value')),
                # Prefetch('permissions', queryset=Permission.filter(deleted_at=None).only('id', 'code'))
            )
        if userdb.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")
        usermod = await query.only(*userdb.select_fields)
    
        if usermod:
            user_dict = await usermod.to_dict(prefetch=True)
            partialkey = s.CACHE_USERNAME.format(id)
            red.set(partialkey, cache.prepareuser_dict(user_dict), clear=True)
        
            if model:
                return userdb.usercomplete(**user_dict), usermod
            return userdb.usercomplete(**user_dict)

    async def get_data(self, force_query=False, debug=False):
        """
        Get the UserDBComplete data whether it be via cache or query. Checks cache first else query.
        :param force_query: Force use query instead of checking the cache
        :param debug:       Debug data for tests
        :return:            UserDBComplete/tuple
        """
        from app.auth import userdb
        
        partialkey = s.CACHE_USERNAME.format(self.id)
        if not force_query and red.exists(partialkey):
            source = 'CACHE'
            user_data = cache.restoreuser_dict(red.get(partialkey))
            user = userdb.usercomplete(**user_data)
        else:
            source = 'QUERY'
            user = await self.get_and_cache(self.id)
    
        if debug:
            return user, source
        return user
    
    async def get_permissions(self, perm_type: Optional[str] = None) -> list:
        """
        Collate all the permissions a user has from groups + user
        :param perm_type:   user or group
        :return:            List of permission codes to match data with
        """
        groups = await self.get_groups()
        group_perms, user_perms = [], []
        
        if perm_type is None or perm_type == 'group':
            # Use perms from cache or else query instead
            if len(groups) == red.exists(*groups):
                for groupname in groups:
                    partialkey = s.CACHE_GROUPNAME.format(groupname)
                    group_perms.append(red.get(partialkey))
            else:
                group_perms = await Permission.filter(groups__name__in=groups)\
                    .values_list('code', flat=True)

        if perm_type is None or perm_type == 'user':
            user_perms = await Permission.filter(permission_users__id=self.id)\
                .values_list('code', flat=True)
        
        return list(set(group_perms + user_perms))

    async def has_perm(self, *perms) -> bool:
        """
        Check if a user has as specific permission code.
        :param perms:   Permission code
        :return:        bool
        """
        if not perms:
            return False
        
        perms = list(filter(None, perms))
        perms = list(filter(lambda x: True if isinstance(x, str) else False, perms))
        
        if not perms:
            return False
        
        return set(perms) <= set(await self.get_permissions())
    
    async def get_groups(self, force_query=False, debug=False) -> Union[list, tuple]:
        """
        Return a user's groups as a list from the cache or not. Uses cache else query.
        :param force_query: Don't use cache
        :param debug:       Return debug data for tests
        :return:            List of groups if not debug
        """
        from app.auth import userdb
        
        partialkey = s.CACHE_USERNAME.format(self.id)
        source = ''
        if not force_query and red.exists(partialkey):
            user_dict = red.get(partialkey)
            source = 'CACHE'
            user_dict = cache.restoreuser_dict(user_dict)
            user = userdb.usercomplete(**user_dict)
        else:
            source = 'QUERY'
            user = await self.get_and_cache(self.id)
        if debug:
            return user.groups, source
        return user.groups
    
    async def has_group(self, *groups) -> bool:
        """
        Check if a user is a part of a group. If 1+ groups are given then it's all or nothing.
        :param groups:  List of group names
        :return:        bool
        """
        allgroups = await self.get_groups()
        if not groups:
            return False
        return set(groups) <= set(allgroups)

    # async def add_permission(self, perms: Union[str, list] = None) -> bool:
    #     """
    #     Add permissions to a user.
    #     :param perms:   Permissions to add
    #     :return:        bool
    #     """
    #     if not perms:
    #         raise ValueError('Type a valid permission to add to this user.')
    #
    #     perms = isinstance(perms, str) and [perms] or perms
    #     try:
    #         permissions = await Permission.filter(code__in=perms).only('id', 'code')
    #         await self.permissions.add(*permissions)
    #         return True
    #     except DBConnectionError:
    #         return False
    

    async def add_group(self, *groups) -> Optional[list]:
        """
        Add groups to a user and update redis
        :param groups:  Groups to add
        :return:        list The user's groups
        """
        from app.auth import userdb
        
        groups = list(filter(None, groups))
        groups = list(filter(valid_str_only, groups))
        if not groups:
            return []
        
        groups = await Group.filter(name__in=groups).only('id', 'name')
        await self.groups.add(*groups)
        names = await Group.filter(group_users__id=self.id)\
            .values_list('name', flat=True)
        
        partialkey = s.CACHE_USERNAME.format(self.id)
        if user_dict := red.get(partialkey):
            user_dict = cache.restoreuser_dict(user_dict)
            user = userdb.usercomplete(**user_dict)
        else:
            user = userdb.get_and_cache(self.id)
        
        user.groups = names
        red.set(partialkey, cache.prepareuser_dict(user.dict()))
        return user.groups
    
    # TESTME: Untested
    async def remove_group(self, *groups):
        user_groups = await self.get_groups()
        groups = list(filter(valid_str_only, groups))
        if not groups:
            return user_groups
    
        for i in [x for x in groups if x in user_groups]:
            user_groups.remove(i)
        
        await self.update_groups(user_groups)
        return user_groups
    
    async def update_groups(self, new_groups: list):
        from app.auth import userdb
        
        new_groups = set(filter(valid_str_only, new_groups))
        valid_groups = set(await Group.filter(name__in=new_groups)\
                           .values_list('name', flat=True))
        if not valid_groups:
            return
        existing_groups = set(await self.get_groups())
        toadd: set = valid_groups - existing_groups
        toremove: set = existing_groups - valid_groups
        
        if toadd:
            toadd_obj = await Group.filter(name__in=toadd).only('id', 'name')
            if toadd_obj:
                await self.groups.add(*toadd_obj)

        if toremove:
            toremove_obj = await Group.filter(name__in=toremove).only('id', 'name')
            if toremove_obj:
                await self.groups.remove(*toremove_obj)

        partialkey = s.CACHE_USERNAME.format(self.id)
        if user_dict := red.get(partialkey):
            user_dict = cache.restoreuser_dict(user_dict)
            user = userdb.usercomplete(**user_dict)
        else:
            user = userdb.get_and_cache(self.id)
        
        user.groups = await self.get_groups(force_query=True)
        red.set(partialkey, cache.prepareuser_dict(user.dict()))
        return user.groups


class UserPermissions(models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='userpermissions')
    permission = fields.ForeignKeyField('models.Permission', related_name='userpermissions')
    author = fields.ForeignKeyField('models.UserMod', related_name='userpermissions_author')
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'auth_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class Group(SharedMixin, models.Model):
    name = fields.CharField(max_length=191, index=True, unique=True)
    summary = fields.TextField(default='')
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    permissions: models.ManyToManyRelation['Permission'] = \
        fields.ManyToManyField('models.Permission', related_name='groups',
                               through='auth_group_permissions', backward_key='group_id')

    class Meta:
        table = 'auth_group'
        manager = ActiveManager()
    
    def __str__(self):
        return modstr(self, 'name')
    
    @classmethod
    async def get_and_cache(cls, group: str) -> list:
        """
        Get a group's permissions and cache it for future use. Replaces data if exists.
        Only one group must be given so each can be cached separately.
        :param group:   Group name
        :param perms:   You can provide the data so querying won't be needed
        :return:        list
        """
        perms = await Permission.filter(groups__name=group).values_list('code', flat=True)
        
        if perms:
            # Save back to cache
            partialkey = s.CACHE_GROUPNAME.format(group)
            red.set(partialkey, perms, clear=True)
            return perms
    
    @classmethod
    async def get_permissions(cls, *groups, debug=False) -> Union[list, tuple]:
        """
        Get a consolidated list of permissions for groups. Uses cache else query.
        :param groups:  Names of groups
        :param debug:   Return debug data for tests
        :return:        List of permissions for that group
        """
        allperms, sources = set(), []
        for group in groups:
            partialkey = s.CACHE_GROUPNAME.format(group)
            if perms := red.get(partialkey):
                sources.append('CACHE')
            else:
                sources.append('QUERY')
                perms = await cls.get_and_cache(group)
            allperms.update(perms)
        
        if debug:
            return list(allperms), sources
        return list(allperms)

    
    # TESTME: Untested
    async def delete_group(self):
        pass
    
    # TESTME: Untested
    async def update_group(self, data: dict):
        pass


class Permission(SharedMixin, models.Model):
    name = fields.CharField(max_length=191, unique=True)
    code = fields.CharField(max_length=191, index=True, unique=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    # groups: fields.ReverseRelation[Group]
    # permission_users: fields.ReverseRelation['UserMod']
    
    class Meta:
        table = 'auth_permission'
        manager = ActiveManager()
    
    def __str__(self):
        return modstr(self, 'name')
    
    @classmethod
    async def add(cls, code: str, name: Optional[str] = ''):
        if not code:
            raise ValueError
        if not name:
            words = code.split('.')
            words = [i.capitalize() for i in words]
            name = ' '.join(words)
        return await cls.create(code=code, name=name)
    
    # # TESTME: Untested
    # @classmethod
    # async def get_groups(cls, *code) -> list:
    #     """
    #     Get the groups which cantain a permission.
    #     :param code:    Permission code
    #     :return:        list
    #     """
    #     if not code:
    #         return []
    #     groups = await Group.filter(permissions__code__in=[*code]).values('name')
    #     return [i.get('name') for i in groups]
    
    # TESTME: Untested
    @classmethod
    async def is_group(cls, perm: str, group: str):
        if not perm or not group:
            return False
        # Get all the group names from cache
        # Save all the groups and perms to cache if they don't exist
        # Check the list
        # Return the result