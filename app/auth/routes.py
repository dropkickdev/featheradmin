import pytz, jwt
from typing import Optional
from datetime import datetime
from pydantic import UUID4, EmailStr
from fastapi import APIRouter, Response, Depends, status, Cookie, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.password import get_password_hash
from tortoise.exceptions import DoesNotExist

from app import ic
from app.auth import (
    TokenMod,
    Authcontrol, Authutils,
    jwtauth, user_db, fapiuser, UniqueFieldsRegistration,
    register_callback, password_after_forgot, password_after_reset, HashMod
)
from .models import UserMod
from app.settings import settings as s
from app import ic      # noqa



# Routes
authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router(register_callback))
# authrouter.include_router(fapiuser.get_verify_router("SECRET"))
# authrouter.include_router(fapi_user.get_reset_password_router(s.SECRET_KEY,
#                                                               after_forgot_password=password_after_forgot,
#                                                               after_reset_password=password_after_reset))
# router.include_router(fapi_user.get_users_router(user_callback))

# exclude this for now
# authrouter.include_router(fapi_user.get_auth_router(jwtauth))

# Don't touch this. This was placed here and not in settings so it won't be edited.
REFRESH_TOKEN_KEY = 'refresh_token'
RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"



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
    user = await fapiuser.db.authenticate(credentials)

    # if not user.is_verified:
    #     return dict(is_verified=False)

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
    if not user.is_verified:
        data.update(dict(details='User is not verified yet so user cannot log in.'))
    return data


@authrouter.get("/logout", dependencies=[Depends(fapiuser.get_current_active_user)])
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


@authrouter.delete('/{id}', dependencies=[Depends(fapiuser.get_current_superuser)])
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


@authrouter.get('/verify/{hash}')
async def verify(hash: str):
    try:
        # Gets the fields in (one query) but you can't update user (bec it's a dict)
        # hashobj = await HashMod.filter(hash=hash, is_active=True, is_used=False)\
        #     .values('id', 'hash', 'expires', is_verified='user__is_verified')
        
        # Get the object (2 queries bec of prefetch_related) but you can update user
        # Do not use only()
        hashobj = await HashMod.get(hash=hash, use_type='register').prefetch_related('user')
        now = datetime.now(tz=pytz.UTC)
        if hashobj.expires and hashobj.expires <= now:
            raise DoesNotExist
        hashobj.user.is_verified = True
        await hashobj.user.save(update_fields=['is_verified'])
        await hashobj.delete()
        return dict(success=True)
    except DoesNotExist:
        return dict(success=False)


@authrouter.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(request: Request, email: EmailStr = Body(..., embed=True)):
    user = await user_db.get_by_email(email)
    
    if user is not None and user.is_active:
        token_data = {"user_id": str(user.id), "aud": RESET_PASSWORD_TOKEN_AUDIENCE}
        token = generate_jwt(token_data, s.RESET_PASSWORD_TTL, s.SECRET_KEY)
        await run_handler(password_after_forgot, user, token, request)
        return True


@authrouter.post("/reset-password")
async def reset_password(request: Request, token: str = Body(...), password: str = Body(...)):
    try:
        data = jwt.decode(token, s.SECRET_KEY, audience=RESET_PASSWORD_TOKEN_AUDIENCE,
                          algorithms=[JWT_ALGORITHM])
        user_id = data.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        try:
            user_uiid = UUID4(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        user = await user_db.get(user_uiid)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        user.hashed_password = get_password_hash(password)
        await user_db.update(user)
        await run_handler(password_after_reset, user, request)
        return True
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )


# @authrouter.get('/readcookie')
# def readcookie(refresh_token: Optional[str] = Cookie(None)):
#     return refresh_token

# @authrouter.get('/password/change')
# def password_change_request(email: EmailStr):
#     # Check if the email exists
#     # Send verification code to email
#     pass
#
#
# @authrouter.get('/password/verify/{hash}')
# def password_change_verify(hash: str):
#     # Check if the hash exists
#     #
#     pass
#
#
# @authrouter.get('/password/update/{hash}')
# def password_update(hash: str):
#     pass