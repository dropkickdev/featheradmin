from typing import Optional, Union
from limeutils import modstr
from tortoise import models, fields
from pydantic import ValidationError

from app import ic, red
from app.settings import settings as s
from app.auth.models.core import DTMixin, SharedMixin
from limeutils import listify


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
    
    groups: fields.ReverseRelation[Group]
    
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
