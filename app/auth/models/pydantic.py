from typing import Optional, Any
from datetime import datetime
from pydantic import validator, Field, EmailStr
from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB

from app.settings import settings as s


class User(BaseUser):
    hashed_password: Optional[str] = ''

class UserCreate(BaseUserCreate):
    """
    REGISTRATION FORM:
    - Anything except the email+password form fields go here
    - Your include= fields from TortoiseUDB can go here (e.g. username)
    """
    pass

class UserUpdate(User, BaseUserUpdate):
    """
    Don't know what this is for yet. Might be fields that you can update...(FOR TESTING MEH)
    """
    pass

class UserDB(User, BaseUserDB):
    """
    ASSIGN DEFAULTS:
    - What the user object will contain from app.auth.current_user
    - Gets data from the db or from the defaults you specify
    - Use this to assign defaults via = or @validator
    - Any fields not a part of BaseUserDB must be queried from the db (or else default is used)
      so add them when instantiating TortoiseUDB in auth.py
    """
    username: Optional[str] = ''
    timezone: Optional[str] = Field(s.USER_TIMEZONE, max_length=10)
    is_verified = s.AUTO_VERIFY
    
    # @validator('fieldname', pre=True, always=True)
    # def demo(cls, val):
    #     return val or yourvalue

class UserDBComplete(UserDB):
    # Can't put these in UserDB since it prevents registration
    groups: set
    permissions: set
    options: dict