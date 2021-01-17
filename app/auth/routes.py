import pytz
from typing import Optional
from datetime import datetime
from pydantic import UUID4
from fastapi import APIRouter, Response, Depends, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi_users.router.common import ErrorCode
from tortoise.exceptions import DoesNotExist

from .Authcontrol import Authcontrol, Authutils
from .models import TokenMod
from app.auth.dependencies import unique_email, unique_username
from app.auth.auth import signup_callback, jwtauth, user_db, fapi_user, UniqueFieldsRegistration
from app.auth.models.user import UserMod
from app.settings import settings as s


# Routes
authrouter = APIRouter()
authrouter.include_router(fapi_user.get_register_router(signup_callback))
# router.include_router(fapi_user.get_users_router(user_callback))

# exclude this for now
# router.include_router(fapi_user.get_auth_router(jwtauth))

# Don't touch this. This was placed here and not in settings so it won't be edited.
REFRESH_TOKEN_KEY = 'refresh_token'




@authrouter.post('/token')
async def new_access_token(response: Response, refresh_token: Optional[str] = Cookie(None)):
    """
    Create a new access_token with the refresh_token cookie. If the refresh_token is still valid
    then a new access_token is generated. If it's expired then it is equivalent to being logged out.

    The refresh_token is renewed for every login to prevent accidental logouts.
    """
    try:
        if refresh_token is None:
            raise Exception

        # TODO: Access the cache instead of querying it
        token = await TokenMod.get(token=refresh_token, is_blacklisted=False) \
            .only('id', 'expires', 'author_id')
        user = await user_db.get(token.author_id)

        mins = Authutils.expires(token.expires)
        if mins <= 0:
            raise Exception
        elif mins <= s.REFRESH_TOKEN_CUTOFF:
            # refresh the refresh_token anyway before it expires
            try:
                token = await Authcontrol.update_refresh_token(user)
            except DoesNotExist:
                token = await Authcontrol.create_refresh_token(user)

            cookie = Authcontrol.refresh_cookie(REFRESH_TOKEN_KEY, token)
            response.set_cookie(**cookie)

        return await jwtauth.get_login_response(user, response)

    except (DoesNotExist, Exception):
        del response.headers['authorization']
        response.delete_cookie(REFRESH_TOKEN_KEY)
        return dict(access_token='')


@authrouter.post("/login")
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends()):
    user = await fapi_user.db.authenticate(credentials, UserMod.starter_fields)

    if not user.is_verified:
        return dict(is_verified=False)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    try:
        token = await Authcontrol.update_refresh_token(user)
    except DoesNotExist:
        token = await Authcontrol.create_refresh_token(user)

    cookie = Authcontrol.refresh_cookie(REFRESH_TOKEN_KEY, token)
    response.set_cookie(**cookie)

    # TODO: Save user's permissions to cache
    # TODO: Save user's groups to cache
    # TODO: Save user data to cache
    data = {
        **await jwtauth.get_login_response(user, response),
        'is_verified': user.is_verified
    }
    return data


@authrouter.get("/logout", dependencies=[Depends(fapi_user.get_current_active_user)])
async def logout(response: Response):
    """
    Logout the user by deleting all tokens. User can log out even if their access_token has already
    expired. Time will tell if this is right. Revert to commented code to only allow un-expired
    tokens to allow logouts.
    """
    # TODO: Delete user's permissions from the cache
    # TODO: Delete user's groups from the cache
    
    del response.headers['authorization']
    response.delete_cookie(REFRESH_TOKEN_KEY)
    return True


@authrouter.delete('/{id}', dependencies=[Depends(fapi_user.get_current_superuser)])
async def delete_user(userid: UUID4):
    """
    Soft-deletes the user instead of hard deleting them.
    """
    try:
        user = await UserMod.get(id=userid).only('id', 'deleted_at')
        user.deleted_at = datetime.now(tz=pytz.UTC)
        await user.save(update_fields=['deleted_at'])
        return True
    except DoesNotExist:
        raise status.HTTP_404_NOT_FOUND


@authrouter.post('/username')
async def check_username(inst: UniqueFieldsRegistration):
    exists = await UserMod.filter(username=inst.username).exists()
    return dict(exists=exists)


@authrouter.post('/email')
async def check_username(inst: UniqueFieldsRegistration):
    exists = await UserMod.filter(email=inst.email).exists()
    return dict(exists=exists)

# @authrouter.get('/readcookie')
# def readcookie(refresh_token: Optional[str] = Cookie(None)):
#     return refresh_token