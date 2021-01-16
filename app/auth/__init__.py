from fastapi import Request
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase
from authcontrol import Authcontrol
from .models.user import User, UserPy, UserCreatePy, UserUpdatePy, UserDBPy

from app.settings import settings as s


jwtauth = JWTAuthentication(secret=s.SECRET_KEY,
                            lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)

user_db = TortoiseUserDatabase(UserDBPy, User)
fapi_user = FastAPIUsers(user_db, [jwtauth], UserPy, UserCreatePy, UserUpdatePy, UserDBPy) # noqa

authcon = Authcontrol(s, jwtauth, user_db, fapi_user)



async def signup_callback(user: UserDBPy, request: Request):      # noqa
    pass
# #     # Add groups to the new user
# #     groups = await Group.filter(name__in=s.USER_GROUPS)
# #     user = await UserTable.get(pk=user.id).only('id')
# #     await user.groups.add(*groups)
#
#
async def user_callback(user: UserDBPy, updated_fields: dict, request: Request):      # noqa
    pass