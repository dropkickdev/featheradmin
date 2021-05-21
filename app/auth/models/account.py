from typing import Union, Optional, List
from limeutils import modstr
from tortoise import fields, models
from tortoise.manager import Manager
from fastapi_users.db import TortoiseBaseUserModel

# from app.auth.models.manager import ActiveManager
from app.auth import models as mod



class UserMod(mod.DTMixin, TortoiseBaseUserModel):
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
        manager = mod.ActiveManager()

    def __str__(self):
        return modstr(self, 'id')