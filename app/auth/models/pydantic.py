from typing import Optional

from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB
from pydantic import validator


class User(BaseUser):
    """
    GETTING THE DATA:
    Any data in UserDB should be here or leave blank."""
    # username: str
    timezone: str
    is_verified: bool


class UserCreate(BaseUserCreate):
    """
    REGISTRATION FORM:
    Anything besides the defaults will go here. Defaults are email password.
    One of your starter_fields might go here.
    """
    # username: str


class UserUpdate(User, BaseUserUpdate):
    pass


class UserDB(User, BaseUserDB):
    """
    WRITING TO DB:
    If the field is in UserCreate then it needs to be here or it won't be written to db.
    If the field is NOT in UserCreate then you'll have to populate it manually for new
    registrations. Populating it here is set via the validator."""
    # username: str                   # Populate via form (UserCreate)
    timezone: Optional[str]         # Populate via validator
    is_verified: Optional[bool]     # Populate via validator
    
    @validator('timezone', pre=True, always=True)
    def default_tz(cls, val):
        return val or '+08:00'
    
    @validator('is_verified', pre=True, always=True)
    def default_ver(cls, val):
        return val or False