from typing import Union, Optional
from fastapi_users.db import TortoiseBaseUserModel, tortoise
from tortoise import fields, models
from limeutils import modstr
from tortoise.exceptions import DBConnectionError

from app import ic
from app.cache import redconn
from app.auth.models.core import DTMixin
from app.auth.models.rbac import Permission, Group



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
            if hasattr(self, field):
                d[field] = getattr(self, field)
                
        # TODO: This ran 3 separate queries. See if you can combine them.
        # UPGRADE: Add the tax to list of keys once in use
        if hasattr(self, 'options'):
            d['options'] = {
                i.name: i.value for i in await self.options.all()
                    .only('id', 'name', 'value', 'is_active') if i.is_active
            }
        if hasattr(self, 'groups'):
            d['groups'] = {i.name for i in await self.groups.all().only('id', 'name')}
        if hasattr(self, 'permissions'):
            d['permissions'] = {i.code for i in await self.permissions.all().only('id', 'code')}
        # ic(d)
        return d

    # TODO: has_perm
    # TEST: Untested
    async def has_perm(self, perm: Union[str, list, tuple]):
        # Collate all perms
        # Get this from redis
        # Save perms of all groups to cache if not exists
        pass
    
    # TODO: has_group
    # TEST: Untested
    async def has_group(self, group: str):
        # Get this from redis
        pass
    
    # TODO: has_groups
    # TEST: Untested
    async def has_groups(self, groups: Union[list, set]):
        # Get this from redis
        pass
    
    async def add_perm(self, perms: Optional[Union[str, list]] = None) -> bool:
        """
        Add permissions to a user.
        :param perms: Permissions to add
        :return:    bool
        """
        if not perms:
            raise ValueError('Type a valid permission to add to this user.')

        perms = isinstance(perms, str) and [perms] or perms
        try:
            permissions = await Permission.filter(code__in=perms).only('id', 'code')
            await self.permissions.add(*permissions)
            return True
        except DBConnectionError:
            return False

    async def add_group(self, groups: Optional[Union[str, list]] = None) -> bool:
        """
        Add groups to a user
        :param groups:  Groups to add
        :return:        bool
        """
        if not groups:
            raise ValueError('Type a valid group to add to this user.')
    
        groups = isinstance(groups, str) and [groups] or groups
        try:
            groups = await Group.filter(name__in=groups).only('id', 'name')
            await self.groups.add(*groups)
            return True
        except DBConnectionError:
            return False
        


class TokenMod(models.Model):
    token = fields.CharField(max_length=128, index=True)
    expires = fields.DatetimeField(index=True)
    is_blacklisted = fields.BooleanField(default=False)
    author = fields.ForeignKeyField('models.UserMod', on_delete=fields.CASCADE,
                                    related_name='author_tokens')
    
    class Meta:
        table = 'auth_token'
    
    def __str__(self):
        return modstr(self, 'token')