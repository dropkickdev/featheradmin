import os
from typing import List
from pydantic import BaseSettings, Field, RedisDsn
from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel
from app.auth.models.user import UserMod, User, UserCreate, UserUpdate, UserDB
from dotenv import load_dotenv



load_dotenv(override=True)


class Base(BaseSettings):
    DEBUG: bool = os.getenv('DEBUG')
    
    # General
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    USE_TZ: bool = True
    TIMEZONE: str = os.getenv('TIMEZONE')
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
    CACHE_URL: RedisDsn = os.getenv('CACHE_URL')
    CACHE_PREFIX: str = os.getenv('CACHE_PREFIX')
    CACHE_VER: str = os.getenv('CACHE_VER')
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
    EMAIL_HOST: str = os.getenv('EMAIL_HOST')
    EMAIL_PORT: int = os.getenv('EMAIL_PORT')
    
    TESTDATA: str = 'This is base data'
    
    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'