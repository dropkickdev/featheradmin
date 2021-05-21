from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase

from app.settings import settings as s
from app.auth import models as mod, routes


jwtauth = JWTAuthentication(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
userdb = TortoiseUserDatabase(mod.UserDB, mod.UserMod)
fapiuser = FastAPIUsers(userdb, [jwtauth], mod.User, mod.UserCreate, mod.UserUpdate, mod.UserDB)
