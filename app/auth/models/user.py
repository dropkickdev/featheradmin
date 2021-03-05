from typing import Union
from fastapi_users.db import TortoiseBaseUserModel, tortoise
from tortoise import fields, models
from limeutils import modstr
# from fastapi_users.db.tortoise import starter_fields

from app import ic
from app.auth.models.core import DTMixin



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
        # ic(self._meta.db_fields)
        for field in self._meta.db_fields:
            if hasattr(self, field):
                d[field] = getattr(self, field)
        
        # TODO: This ran 3 separate queries. Combine them.
        # ic(self._meta.backward_fk_fields)
        d['options'] = {
            i.name: i.value for i in await self.options.all()
                .only('name', 'value', 'is_active') if i.is_active
        }
        d['groups'] = [i.name for i in await self.groups.all().only('id', 'name')]
        d['permissions'] = [i.code for i in await self.permissions.all().only('code')]
        return d
    
    # TODO: has_perm
    async def has_perm(self, perm_code: Union[str, list, tuple]):
        pass
    
    # TODO: has_group
    async def has_group(self, group_name: Union[str, list, tuple]):
        pass


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