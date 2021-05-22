from typing import Union, Optional, List
from limeutils import modstr
from tortoise import fields, models
from tortoise.manager import Manager
from fastapi_users.db import TortoiseBaseUserModel
from tortoise.exceptions import BaseORMException
from redis.exceptions import RedisError

# from app.authentication.models.manager import ActiveManager
from app import settings as s, exceptions as x
from app.auth import DTMixin, ActiveManager, SharedMixin
from app.cache import red
from app.validation import UpdateGroup, UpdatePermission



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

    full = Manager()

    class Meta:
        table = 'auth_user'
        manager = ActiveManager()

    def __str__(self):
        return modstr(self, 'id')


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
        perms = perms or []
        
        if perms:
            # Save back to cache
            partialkey = s.CACHE_GROUPNAME.format(group)
            red.set(partialkey, perms, ttl=-1, clear=True)
            
            # TODO: Remove the group from this key if a group is deleted
            grouplist = red.exists('groups') and red.get('groups') or []
            if group not in grouplist:
                grouplist.append(group)
                red.set('groups', grouplist, clear=True)
        return perms
    
    @classmethod
    async def get_permissions(cls, *groups, debug=False) -> Union[list, tuple]:
        """
        Get a consolidated list of permissions for groups. Uses cache else query.
        :param groups:  Names of groups
        :param debug:   Return debug data for tests
        :return:        List of permissions for that group
        """
        debug = debug if s.DEBUG else False
        allperms, sources = set(), []
        for group in groups:
            partialkey = s.CACHE_GROUPNAME.format(group)
            if perms := red.get(partialkey):
                sources.append('CACHE')
            else:
                sources.append('QUERY')
                perms = await cls.get_and_cache(group)
            # ic(group, perms)
            if perms:
                allperms.update(perms)
        
        if debug:
            return list(allperms), sources
        return list(allperms)
    
    @classmethod
    async def delete_group(cls, name: str) -> Optional[list]:
        """
        Delete a group
        :param name:    Name of group
        :return:        List of groups remaining
        """
        try:
            # Delete from db
            if name:
                if group := await Group.get_or_none(name=name).only('id'):
                    await group.delete()
                else:
                    return
                
                # Update cache
                partialkey = s.CACHE_GROUPNAME.format(name)
                red.delete(partialkey)
                if grouplist := red.get('groups'):
                    grouplist = list(filter(lambda y: y != name, grouplist))
                    red.set('groups', grouplist, clear=True)
                    return grouplist
        except (BaseORMException, RedisError):
            raise x.BadError()
    
    async def update_group(self, group: UpdateGroup):
        """
        Update the name and summary of a group.
        :param:     Pydantic instance with fields: id, name, summary
        :return:    dict
        """
        self.name = group.name
        self.summary = group.summary
        await self.save(update_fields=['name', 'summary'])


class Permission(SharedMixin, models.Model):
    name = fields.CharField(max_length=191, unique=True)
    code = fields.CharField(max_length=30, index=True, unique=True)
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
    
    @classmethod
    async def get_groups(cls, *code) -> list:
        """
        Get the groups which contain a permission.
        :param code:    Permission code
        :return:        list
        """
        if not code:
            return []
        groups = await Group.filter(permissions__code__in=[*code]).values_list('name', flat=True)
        return list(set(groups))
    
    @classmethod
    async def update_permission(cls, perm: UpdatePermission):
        if perminst := await Permission.get_or_none(pk=perm.id).only('id', 'code', 'name'):
            ll = []
            if perm.code is not None:
                ll.append('code')
                perminst.code = perm.code
            if perm.name is not None:
                ll.append('name')
                perminst.name = perm.name
            if ll:
                await perminst.save(update_fields=ll)
