import secrets
from typing import Optional, Union
from tortoise.query_utils import Prefetch
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.user import UserNotExists
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import generate_jwt
from pydantic import BaseModel, EmailStr, Field, SecretStr, UUID4

from app import ic, red, cache      # noqa
from app.settings import settings as s
from .models import UserMod, User, UserCreate, UserUpdate, UserDB, UserDBComplete
from .models import Group, Permission
from app.authentication.models.core import Option
from .Mailman import Mailman
from .FastAPIUsers.JwtAuth import JwtAuth
from .FastAPIUsers.FapiUsers import FapiUsers
from .FastAPIUsers.tortoise import TortoiseUDB




