from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase

from app.settings import settings as s
from app.auth import UserMod, User, UserCreate, UserUpdate, UserDB


userdb = TortoiseUserDatabase(UserDB, UserMod)
jwtauth = JWTAuthentication(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
fapiuser = FastAPIUsers(userdb, [jwtauth], User, UserCreate, UserUpdate, UserDB)
