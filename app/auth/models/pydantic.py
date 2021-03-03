from typing import Optional
from datetime import datetime
from pydantic import validator, Field, EmailStr
from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB

from app.settings import settings as s



class User(BaseUser):
    """
    USER OBJECT ATTRS:
    - Fields that go here must have a value (you can populate them in UserDB or UserCreate)
    - This reprents the user object. If you want any user data to be a part of that object
      besides BaseUser fields then add them here (TEST IF TRUE).
    - If you're fine with the BaseUser fields then leave this blank
    """
    # username: str
    timezone: str
    email: EmailStr


class UserCreate(BaseUserCreate):
    """
    REGISTRATION FORM:
    - Anything except the email+password form fields go here
    - Your starter_fields can go here (e.g. username)
    """
    # username: str
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
    - Use this to assign defaults via = or @validator
    """
    username: Optional[str] = ''
    timezone: Optional[str] = Field('+08:00', max_length=10)
    is_verified = s.AUTO_VERIFY
    
    # @validator('fieldname', pre=True, always=True)
    # def demo(cls, val):
    #     return val or yourvalue
