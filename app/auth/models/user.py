from typing import Union, Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.db import TortoiseBaseUserModel, tortoise
from tortoise import fields, models
from tortoise.query_utils import Prefetch
from limeutils import modstr
from tortoise.exceptions import DBConnectionError
from contextlib import contextmanager
from ast import literal_eval

from app import ic, red
from app.cache import red, makesafe
from app.auth.models.core import DTMixin
from app.auth.models.rbac import Permission, Group



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
    
    # Additional fields
    # starter_fields = ['timezone']
    
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
    
    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            if hasattr(self, field) and field not in ['created_at', 'deleted_at', 'updated_at']:
                d[field] = getattr(self, field)
                
        # TODO: This ran 3 separate queries. See if you can combine them.
        # UPGRADE: Add the tax to list of keys once in use
        if hasattr(self, 'options'):
            d['options'] = {
                i.name: i.value for i in await self.options.all()
                    .only('id', 'name', 'value', 'is_active') if i.is_active
            }
        if hasattr(self, 'groups'):
            d['groups'] = [i.name for i in await self.groups.all().only('id', 'name')]
        if hasattr(self, 'permissions'):
            d['permissions'] = [i.code for i in await self.permissions.all().only('id', 'code')]
        # ic(d)
        return d

    # TODO: has_perm
    # TEST: Untested
    async def has_perms(self, *perms):
        # groups = await self.get_groups()
        # allperms = await Permission.filter(groups__id=1)
        # ic(allperms)
        # Get this from redis
        # Save perms of all groups to cache if not exists
        # return await current_user()
        return 'foo'
    
    # async def _gather_permissions(self):
    #     groups = red.get(self.id)
    #     from_groups = await Permission.all().prefetch_related(
    #         Prefetch('groups', queryset=Group.filter(name__in=[]))
    #     ).values('code')
    
    async def get_groups(self) -> list:
        """Return the groups of the user as a list"""
        groups = red.get(str(self.id), only='groups').get('groups')
        groups = literal_eval(groups)
        return groups
    
    async def get_permissions(self):
        groups = await self.get_groups()
        # x = await Permission.filter(groups__name__in=groups)
        x = await Group.filter(permissions__id=1)
        ic(x)
    
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
        

    # # TODO: has_groups
    # # TEST: Untested
    # async def has_groups(self, groups: Union[list, set]):
    #     # Get this from redis
    #     pass
    #
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
            red.set(str(self.id), dict(groups=makesafe(names)))
            
            return names
        except DBConnectionError:
            return []
        


class TokenMod(models.Model):
    token = fields.CharField(max_length=128, unique=True)
    expires = fields.DatetimeField(index=True)
    is_blacklisted = fields.BooleanField(default=False)
    author = fields.ForeignKeyField('models.UserMod', on_delete=fields.CASCADE,
                                    related_name='author_tokens')
    
    class Meta:
        table = 'auth_token'
    
    def __str__(self):
        return modstr(self, 'token')