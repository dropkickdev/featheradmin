import os
from typing import List, Dict
from pydantic import BaseSettings, Field, RedisDsn, EmailStr
from dotenv import load_dotenv



load_dotenv(override=True)


class Base(BaseSettings):
    DEBUG: bool = os.getenv('DEBUG')
    SITE_NAME: str = 'Feather Admin'
    
    # General
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    SECRET_KEY_EMAIL: str = os.getenv('SECRET_KEY_EMAIL')
    USE_TZ: bool = True
    TIMEZONE: str = 'UTC'
    LANGUAGE_CODE: str = 'en-us'

    # Authentication
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE: int = 60 * 15              # seconds (15 mins)
    REFRESH_TOKEN_EXPIRE: int = 3600 * 24 * 15      # seconds (15 days)
    REFRESH_TOKEN_CUTOFF: int = 30                  # minutes
    SESSION_COOKIE_AGE: int = 3600 * 24 * 15        # seconds
    VERIFY_EMAIL_TTL: int = 3600 * 3                # seconds
    RESET_PASSWORD_TTL: int = 60 * 30               # seconds
    
    # Database
    # Refer to app.settings.db.py
    
    # Cache
    USE_CACHE: bool = True
    CACHE_TTL: int = 3600 * 24 * 15
    CACHE_CONFIG: dict = {
        "default": {
            'pre':  os.getenv('CACHE_PREFIX'),
            'ver':  os.getenv('CACHE_VERSION'),
            'ttl':  os.getenv('CACHE_TTL', CACHE_TTL),
        }
    }
    CACHE_GROUPNAME: str = 'group-{}'
    CACHE_USERNAME: str = 'user-{}'
    CACHE_PERMNAME: str = 'permission-{}'
    
    # Account
    USERNAME_MIN: int = Field(4, ge=4, le=10)
    PASSWORD_MIN: int = Field(6, ge=10, le=20)
    USER_GROUPS: List[str] = ['AccountGroup', 'ContentGroup']
    AUTO_VERIFY: bool = False
    VERIFY_EMAIL: bool = True
    EMAIL_SENDER: EmailStr = 'accounts@featheradmin.com'
    USER_TIMEZONE: str = os.getenv('USER_TIMEZONE', '+08:00')
    
    # Email
    EMAIL_PORT: int = os.getenv('EMAIL_PORT')
    EMAIL_HOST: str = os.getenv('EMAIL_HOST')
    EMAIL_HOST_USER: str = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASS: str = os.getenv('EMAIL_HOST_PASS')
    
    # Form/Notice URLs
    NOTICE_HEADER: dict = {'X-Allow-Notice': 'true'}
    FORM_RESET_PASSWORD: str = os.getenv('FORM_RESET_PASSWORD', '/reset-password-form')
    NOTICE_VERIFY_REGISTER_OK: str = os.getenv('NOTICE_VERIFY_REGISTER_OK', '/n/verify-register-ok')
    NOTICE_VERIFY_REGISTER_FAIL: str = os.getenv('NOTICE_VERIFY_REGISTER_FAIL', '/n/verify-register-fail')
    NOTICE_TOKEN_EXPIRED: str = os.getenv('NOTICE_TOKEN_EXPIRED', '/n/token-expired')
    NOTICE_TOKEN_BAD: str = os.getenv('NOTICE_TOKEN_BAD', '/n/token-bad')
    NOTICE_USER_ALREADY_VERIFIED: str = os.getenv('NOTICE_USER_ALREADY_VERIFIED',
                                                  '/n/user-already-verified')
    
    TESTDATA: str = 'This is base data'
    
    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'