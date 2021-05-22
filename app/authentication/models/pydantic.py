# from typing import Optional, Any
# from datetime import datetime
from fastapi_users import models
# from pydantic import validator, Field, EmailStr
# from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB
from tortoise.contrib.pydantic import PydanticModel

from .account import UserMod
# from app import red, ic
# from app.settings import settings as s
# from .account import UserMod, Group








class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserMod












# class User(BaseUser):
#     hashed_password: Optional[str] = ''
#
#
# class UserCreate(BaseUserCreate):
#     """
#     REGISTRATION FORM:
#     - Anything except the email+password form fields go here
#     - Your include= fields from TortoiseUDB can go here (e.g. username)
#     """
#     @validator('password')
#     def valid_password(cls, v: str):
#         if len(v) < s.PASSWORD_MIN:
#             raise ValueError(f'Password should be at least {s.PASSWORD_MIN} characters')
#         return v
#
#     # @validator('username')
#     # def valid_username(cls, v: str):
#     #     if len(v) < s.USERNAME_MIN:
#     #         raise ValueError(f'Username should be at least {s.USERNAME_MIN} characters')
#     #     return v
#
# class UserUpdate(User, BaseUserUpdate):
#     """
#     Don't know what this is for yet. Might be fields that you can update...(FOR TESTING MEH)
#     """
#     pass
#
# class UserDB(User, BaseUserDB):
#     """
#     ASSIGN DEFAULTS:
#     - What the user object will contain from app.authentication.current_user
#     - Gets data from the db or from the defaults you specify
#     - Use this to assign defaults via = or @validator
#     - Any fields not a part of BaseUserDB must be queried from the db (or else default is used)
#       so add them when instantiating TortoiseUDB in auth_routes.py
#     """
#     username: Optional[str] = ''
#     timezone: Optional[str] = Field(s.USER_TIMEZONE, max_length=10)
#     is_verified = s.AUTO_VERIFY
#
#     # @validator('fieldname', pre=True, always=True)
#     # def demo(cls, val):
#     #     return val or yourvalue
#
#     async def has_perm(self, *perms, superuser=True) -> bool:
#         """
#         Check if user has permission with exception of the superuser.
#         :param perms:   Permission code/s
#         :return:        bool
#         """
#         if not perms:
#             return False
#         allperms = await self.get_perms()
#         if allperms:
#             if superuser:
#                 # ic('foo')
#                 return self.is_superuser or set(perms) <= set(allperms)
#             return set(perms) <= set(allperms)
#
#     async def get_perms(self) -> list:
#         """
#         Get perms from the cache else query. Does not merge with user perms for now.
#         :return: List of perms
#         """
#         allperms = set()
#
#         # Get group perms from cache
#         for group in self.groups:                                                   # noqa
#             group_partialkey = s.CACHE_GROUPNAME.format(group)
#             if red.exists(group_partialkey):
#                 cached_perms = red.get(group_partialkey)
#                 allperms.update(cached_perms)
#             else:
#                 queried_perms = await Group.get_and_cache(group)
#                 allperms.update(queried_perms)
#         # Include any user perms if any
#         allperms.update(self.permissions)                                           # noqa
#         return list(allperms)
#
#     # This works but not needed
#     # async def get_data(self):
#     #     """
#     #     Get UserDBComplete from cache or query.
#     #     :return: UserDBComplete or None
#     #     """
#     #     partialkey = s.CACHE_USERNAME.format(self.id)
#     #     user = red.get(partialkey) or None
#     #     if user:
#     #         # ic('CACHE')
#     #         user_dict = cache.restoreuser_dict(user)
#     #         user = UserDBComplete(**user_dict)
#     #     else:
#     #         # ic('QUERY')
#     #         usermod = await UserMod.get_or_none(pk=self.id).only('id')
#     #         user = await usermod.get_data()
#     #         # No need for restoreuser_dict since it's already UserDBComplete
#     #     return user
#
# class UserDBComplete(UserDB):
#     # Can't put these in UserDB since it prevents registration
#     id: str
#     groups: list
#     options: dict
#     permissions: list
#
#     # Make id a str instead of UUID
#     @validator('id', pre=True, always=True)
#     def just_str(cls, val):
#         return str(val)
