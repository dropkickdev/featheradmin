import secrets, pytz
from datetime import datetime, timedelta
from fastapi_users import FastAPIUsers
from fastapi.security import OAuth2PasswordBearer
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

current_user = fapiuser.current_user()
tokenonly = OAuth2PasswordBearer(tokenUrl='token')

REFRESH_TOKEN_KEY = 'refresh_token'         # Don't change this. This is hard-coded as a variable.


def generate_refresh_token(nbytes: int = 32):
    return secrets.token_hex(nbytes=nbytes)


async def create_refresh_token(user) -> dict:
    """
    Create and save a new refresh token
    :param user Pydantic model for the user
    """
    user = await UserMod.get(pk=user.id).only('id')
    refresh_token = generate_refresh_token()
    expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=s.REFRESH_TOKEN_EXPIRE)

    await TokenMod.create(token=refresh_token, expires=expires, author=user)
    return {
        'value': refresh_token,
        'expires': expires,
    }


async def update_refresh_token(user, token: TokenMod = None) -> dict:
    """
    Update the refresh token of the user
    :param user     Pydantic model for the user
    :param token    Use an existing TokenMod instance if there is one and save a query
    """
    refresh_token = generate_refresh_token()
    expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=s.REFRESH_TOKEN_EXPIRE)
    
    if not token:
        token = await TokenMod.get(author_id=user.id, is_blacklisted=False) \
            .only('id', 'token', 'expires')
    
    token.token = refresh_token
    token.expires = expires
    await token.save(update_fields=['token', 'expires'])
    return {
        'value': refresh_token,
        'expires': expires,
    }


def refresh_cookie(name: str, token: dict, **kwargs):
    if token['expires'] <= datetime.now(tz=pytz.UTC):
        raise ValueError(_('Cookie expires date must be greater than the date now'))

    expires = token['expires'] - datetime.now(tz=pytz.UTC)
    cookie_data = {
        'key': name,
        'value': token['value'],
        'httponly': True,
        'expires': expires.seconds,
        'path': '/',
        **kwargs,
    }
    if not s.DEBUG:
        cookie_data.update({
            'secure': True
        })
    return cookie_data