from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase

from app.settings import settings as s
from app.auth import models, routes


userdb = TortoiseUserDatabase(models.UserDB, models.UserMod)
jwtauth = JWTAuthentication(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
fapiuser = FastAPIUsers(userdb, [jwtauth], models.User, models.UserCreate, models.UserUpdate,
                        models.UserDB)
