from typing import List, Optional
from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn
from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel
from app.auth.models.user import User, UserPy, UserCreatePy, UserUpdatePy, UserDBPy


class Base(BaseSettings):
    DEBUG: bool = False
    
    # General
    SECRET_KEY: str = Field(..., min_length=32)
    USE_TZ: bool = True
    TIMEZONE: str = 'UTC'
    LANGUAGE_CODE: str = 'en-us'

    # Authentication
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE: int = 60 * 15              # seconds (15 mins)
    REFRESH_TOKEN_EXPIRE: int = 60 * 60 * 24 * 30   # seconds (30 days)
    REFRESH_TOKEN_CUTOFF: int = 30                  # minutes
    SESSION_COOKIE_AGE: int = 1209600  # seconds

    # Database
    # Refer to app.settings.db.py
    
    # Cache
    USE_CACHE: bool = True
    CACHE_TTL: int = 3600 * 24
    CACHE_URL: RedisDsn = 'redis://127.0.0.1:6379/0'
    CACHE_PREFIX: str = Field('DBZ', min_length=3, max_length=10)
    CACHE_VER: str = Field('', max_length=5)
    CACHES: dict = {
        "default": {
            "LOCATION": CACHE_URL,
            "KEY_PREFIX": CACHE_PREFIX,
            "VERSION": CACHE_VER,
            "OPTIONS": {}
        }
    }
    
    # Account
    USERNAME_MIN: int = Field(4, ge=4, le=10)
    PASSWORD_MIN: int = Field(10, ge=10, le=20)
    USER_GROUPS: List[str] = ['AccountGroup', 'ProfileGroup']
    
    # Email
    EMAIL_HOST: str = Field('localhost')
    EMAIL_PORT: int = Field(1025)
    
    # Authcontrol
    # USER_TABLE: TortoiseBaseUserModel = User
    # USER_PYDANTIC_MODEL: models.BaseUser = UserPy
    # USERCREATE_PYDANTIC_MODEL: models.BaseUserCreate = UserCreatePy
    # USERUPDATE_PYDANTIC_MODEL: models.BaseUserUpdate = UserUpdatePy
    # USERDB_PYDANTIC_MODEL: models.BaseUserDB = UserDBPy

    TESTDATA: str = 'This is base data'
    
    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'