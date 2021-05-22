from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase

from . import settings as s
from .authentication.models.account import UserMod
from .authentication.models.pydantic import *
from .authentication.models.manager import *
from .authentication.models.core import *
from .authentication.models.account import *
from .authentication.models.pydantic import *


userdb = TortoiseUserDatabase(UserDB, UserMod)
jwtauth = JWTAuthentication(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
fapiuser = FastAPIUsers(userdb, [jwtauth], User, UserCreate, UserUpdate, UserDB)