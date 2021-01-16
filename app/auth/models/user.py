from typing import Optional, Union
from pydantic import validator
from pydantic import BaseModel, EmailStr, Field
from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB
from fastapi_users.db import TortoiseBaseUserModel, tortoise
from tortoise import fields, models
from limeutils import model_str

from app.auth.models.core import DTMixin
from app import settings as s

"""
DB
"""

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
    
    is_verified = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)
    
    groups = fields.ManyToManyField('models.Group', related_name='group_users',
                                    through='auth_user_groups', backward_key='user_id')
    permissions = fields.ManyToManyField('models.Permission', related_name='permission_users',
                                         through='auth_user_permissions', backward_key='user_id')
    
    starter_fields = [*tortoise.starter_fields, 'timezone', 'is_verified']
    
    class Meta:
        table = 'auth_user'
        
    def __str__(self):
        return model_str(self, 'username')
    
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
        for field in self.starter_fields:
            d[field] = getattr(self, field)
        return d
    
    # TODO: has_perm
    async def has_perm(self, perm_code: Union[str, list, tuple]):
        pass
    
    # TODO: has_group
    async def has_group(self, group_name: Union[str, list, tuple]):
        pass




"""
PYDANTIC
"""


class User(BaseUser):
    """
    GETTING THE DATA:
    Will be a part of the user object along with the default default fields.
    Your new fields in starter_fields might go here."""
    # username: str
    timezone: str
    is_verified: bool


class UserCreate(BaseUserCreate):
    """
    REGISTRATION FORM:
    Anything besides the defaults will go here. Defaults are email password.
    One of your starter_fields might go here.
    """
    username: str
    pass


class UserUpdate(User, BaseUserUpdate):
    pass


class UserDB(User, BaseUserDB):
    """
    WRITING TO DB:
    If the field is in UserCreate then it needs to be here or it won't be written to db.
    If the field is NOT in UserCreate then you'll have to populate it manually for new
    registrations. Populating it here is set via the validator."""
    username: str                   # Populate via form (UserCreate)
    timezone: Optional[str]         # Populate via validator
    is_verified: Optional[bool]     # Populate via validator
    
    @validator('timezone', pre=True, always=True)
    def default_tz(cls, val):
        return val or '+08:00'
    
    @validator('is_verified', pre=True, always=True)
    def default_ver(cls, val):
        return val or False


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field(..., min_length=s.USERNAME_MIN)
    password: str   = Field(..., min_length=s.PASSWORD_MIN)