from typing import Union, Optional, List
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.db import TortoiseBaseUserModel
from tortoise import fields, models
from tortoise.query_utils import Prefetch
from limeutils import modstr
from tortoise.exceptions import DBConnectionError
from ast import literal_eval

from app.auth.models import SharedMixin
from app.settings import settings as s
from app import cache
from app.cache import red, makesafe
# from app.auth import userdb
from app.auth.models.core import DTMixin, Option

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
    
    class Meta:
        table = 'auth_user'
        
    def __str__(self):
        return modstr(self, 'username')
    
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

    # async def to_dict(self, exclude: Optional[List[str]] = None) -> dict:
    #     """
    #     Convert a UserMod instance into a dict. Only a select number of fields are selected.
    #     :param exclude: Fields not to explicitly include
    #     :return:        dict
    #     """
    #     d = {}
    #     exclude = ['created_at', 'deleted_at', 'updated_at'] if exclude is None else exclude
    #     for field in self._meta.db_fields:
    #         if hasattr(self, field) and field not in exclude:
    #             d[field] = getattr(self, field)
    #             if field == 'id':
    #                 d[field] = str(d[field])
    #
    #     # UPGRADE: Add the tax to list of keys once in use
    #     if hasattr(self, 'groups'):
    #         d['groups'] = [i.name for i in self.groups]
    #     if hasattr(self, 'options'):
    #         d['options'] = {i.name: i.value for i in self.options}
    #     # if hasattr(self, 'permissions'):
    #     #     d['permissions'] = [i.code for i in self.permissions]
    #     return d
    
    
    async def to_dict(self, exclude: Optional[List[str]] = None, prefetch=False) -> dict:
        """
        Convert a UserMod instance into a dict. Only a select number of fields are selected.
        :param exclude: Fields not to explicitly include
        :return:        dict
        """
        d = {}
        exclude = ['created_at', 'deleted_at', 'updated_at'] if exclude is None else exclude
        for field in self._meta.db_fields:
            if hasattr(self, field) and field not in exclude:
                d[field] = getattr(self, field)
                if field == 'id':
                    d[field] = str(d[field])
        # TODO: This ran 3 separate queries. See if you can combine them.
        # UPGRADE: Add the tax to list of keys once in use
        if hasattr(self, 'groups'):
            if prefetch:
                d['groups'] = [i.name for i in self.groups]
            else:
                d['groups'] = [i.name for i in await self.groups.all().only('id', 'name')]
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

    @classmethod
    async def get_and_cache(cls, id: str, model=False) -> Union[dict, tuple]:
        """
        Get a user's cachable data and cache it for future use. Replaces data if exists.
        Similar to the dependency user_data.
        :param id:      User id as str
        :param model:   Also return the UserMod instance
        :return:        DOESN'T NEED cache.restoreuser() since data is from the db not redis.
                        The id key in the hash is already formatted to a str from UUID.
        """
        select = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
        select += ['timezone', 'username']
        query = cls.get_or_none(pk=id)\
            .prefetch_related(
                Prefetch('groups', queryset=Group.filter(deleted_at=None).only('id', 'name')),
                Prefetch('options', queryset=Option.filter(is_active=True)
                         .only('user_id', 'name', 'value')),
                # Prefetch('permissions', queryset=Permission.filter(deleted_at=None).only('id', 'code'))
            )
        
        # if userdb.oauth_account_model is not None:
        #     query = query.prefetch_related("oauth_accounts")
            
        query = query.only(*select)
        
        user = await query

        if user:
            user_dict = await user.to_dict(prefetch=True)
            partialkey = s.CACHE_USERNAME.format(str(id))
            red.set(partialkey, cache.prepareuser(user_dict), clear=True)
            
            if model:
                return user_dict, user
            return user_dict
    
    # TESTME: Untested
    async def has_perms(self, *perms) -> bool:
        if not perms:
            return False
        ret = set(perms) <= await self.get_permissions()
        return ret
    
    # TESTME: Untested
    async def get_permissions(self, perm_type=None) -> set:
        """
        Collate all the permissions a user has from groups + user
        :return:    Set of permission codes to match data with
        """
        groups = await self.get_groups()
        user_group_perms = []
        user_solo_perms = []
        
        if perm_type is None or perm_type == 'group':
            # Use perms from cache or else query instead
            if len(groups) == red.exists(*groups):
                for groupname in groups:
                    user_group_perms.append(red.get(f'group-{groupname}'))
            else:
                user_group_perms = await Permission.filter(groups__name__in=groups).values('code')

        if perm_type is None or perm_type == 'user':
            user_solo_perms = await Permission.filter(permission_users__id=self.id).values('code')
            
        ret = {i.get('code') for i in user_group_perms + user_solo_perms}
        return ret
    
    
    # async def _gather_permissions(self):
    #     groups = red.get(self.id)
    #     from_groups = await Permission.all().prefetch_related(
    #         Prefetch('groups', queryset=Group.filter(name__in=[]))
    #     ).values('code')
    
    # async def add_perms(self, *args):
    #     return await super().add_perms(*args)
    #
    # async def remove_perms(self, *args):
    #     return await super().remove_perms(*args)
    
    # TESTME: Untested
    async def get_groups(self) -> list:
        """Return the groups of the user as a list from the cache"""
        groups = red.get(str(f'user-{self.id}'), only='groups').get('groups')
        groups = literal_eval(groups)
        return groups
    
    # TESTME: Untested
    async def has_group(self, *groups):
        """
        Check if a user is a part of a group. If 1+ groups are given then it's all or nothing.
        :param groups:  List of group names
        :return:        bool
        """
        if not groups:
            return False
        allgroups = await self.get_groups()
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
    
    # TESTME: Untested
    async def add_group(self, *groups) -> list:
        """
        Add groups to a user and update redis
        :param groups:  Groups to add
        :return:        bool
        """
        try:
            groups = await Group.filter(name__in=groups).only('id', 'name')
            await self.groups.add(*groups)
            allgroups = await Group.filter(group_users__id=self.id).values('name')
            
            names = [i.get('name') for i in allgroups]
            red.set(s.CACHE_USERNAME.format(str(self.id)), dict(groups=makesafe(names)))
            
            return names
        except DBConnectionError:
            return []
    
    # TESTME: Untested
    async def remove_group(self, *groups):
        pass


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
    
    def __str__(self):
        return modstr(self, 'name')
    
    @classmethod
    async def get_and_cache(cls, group: str, perms: list = None) -> list:
        """
        Get a group's permissions and cache it for future use. Replaces data if exists.
        Only one group must be given so each can be cached separately.
        :param group:   Group name
        :param perms:   You can provide the data so querying won't be needed
        :return:        list
        """
        if perms is None:
            perms = await Permission.filter(groups__name=group).values('code')
            perms = [i.get('code') for i in perms]

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
        allperms = set()
        sources = []
        for group in groups:
            name = s.CACHE_GROUPNAME.format(group)
            if perms := red.get(name):
                sources.append('cache')
            else:
                sources.append('query')
                perms = await cls.get_and_cache(group)
            allperms.update(perms)
        
        if debug:
            return list(allperms), sources
        else:
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
    
    # TESTME: Untested
    @classmethod
    async def get_groups(cls, *code) -> list:
        """
        Get the groups which cantain a permission.
        :param code:    Permission code
        :return:        list
        """
        if not code:
            return []
        groups = await Group.filter(permissions__code__in=[*code]).values('name')
        return [i.get('name') for i in groups]
    
    # TESTME: Untested
    @classmethod
    async def is_group(cls, perm: str, group: str):
        if not perm or not group:
            return False
        # Get all the group names from cache
        # Save all the groups and perms to cache if they don't exist
        # Check the list
        # Return the result