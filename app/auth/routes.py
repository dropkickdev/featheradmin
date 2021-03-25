import jwt
from typing import Optional, cast
from pydantic import UUID4, EmailStr
from fastapi import APIRouter, Response, Depends, status, Body, Request, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi_users.utils import JWT_ALGORITHM
from fastapi_users.user import UserNotExists, UserAlreadyVerified
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.password import get_password_hash
from tortoise.exceptions import DoesNotExist

from app import ic      # noqa
from app.auth import (
    Authcontrol, Authutils, TokenMod,
    jwtauth, userdb, fapiuser, UniqueFieldsRegistration, current_user,     # noqa
    register_callback, send_password_email,
)
from .models import User, UserMod
from app.settings import settings as s



# Routes
authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router(register_callback))  # register
# authrouter.include_router(fapiuser.get_reset_password_router(s.SECRET_KEY_TEMP,
#                                                              after_forgot_password=password_after_forgot,
#                                                              after_reset_password=password_after_reset))

# Do not use
# authrouter.include_router(fapiuser.get_auth_router(jwtauth))    # login, logout
# authrouter.include_router(fapiuser.get_verify_router(s.SECRET_KEY, s.VERIFY_EMAIL_TTL))
# router.include_router(fapi_user.get_users_router(user_callback))

# DON'T TOUCH THIS. This was placed here and not in settings so it won't be edited.
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
        user = await userdb.get(token.author_id)

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
    
    if user is None or not user.is_active or not user.is_verified:
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

    # TODO: Check if user data is in cache in accordance with UserDB
    
    data = {
        **await jwtauth.get_login_response(user, response),
        'is_verified': user.is_verified
    }
    if not user.is_verified:
        data.update(dict(details='User is not verified yet so user cannot log in.'))
    return data


@authrouter.post("/logout", dependencies=[Depends(current_user)])
async def logout(response: Response):
    """
    Logout the user by deleting all tokens. Only unexpired tokens can logout.
    """
    # TODO: Delete user's permissions from the cache
    # TODO: Delete user's groups from the cache

    del response.headers['authorization']
    response.delete_cookie(REFRESH_TOKEN_KEY)
    return True


@authrouter.get("/verify", response_model=User)
async def verify(_: Request, t: Optional[str] = None):
    """
    Verify email verification for new registrations
    """
    if not t:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    try:
        data = jwt.decode(t, s.SECRET_KEY, audience=VERIFY_USER_TOKEN_AUDIENCE,
                          algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_TOKEN_EXPIRED,
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    user_id = data.get("user_id")
    email = cast(EmailStr, data.get("email"))
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    try:
        user_check = await fapiuser.get_user(email)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    try:
        user_uuid = UUID4(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    if user_check.id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    
    try:
        user = await fapiuser.verify_user(user_check)
    except UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )
    
    return user


@authrouter.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(_: Request, email: EmailStr = Body(..., embed=True)):
    user = await userdb.get_by_email(email)
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    await send_password_email(user,
                              'app/auth/templates/emails/account/password_verify_text.jinja2',
                              'app/auth/templates/emails/account/password_verify_html.jinja2')


@authrouter.post("/reset-password")
async def reset_password(_: Request, token: str = Body(...), password: str = Body(...)):
    try:
        data = jwt.decode(token, s.SECRET_KEY_TEMP, audience=RESET_PASSWORD_TOKEN_AUDIENCE,
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
        
        user = await userdb.get(user_uiid)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        user.hashed_password = get_password_hash(password)
        await userdb.update(user)
        return True
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )
    

# @authrouter.delete('/{id}', dependencies=[Depends(fapiuser.get_current_superuser)])
# async def delete_user(userid: UUID4):
#     """
#     Soft-deletes the user instead of hard deleting them.
#     """
#     try:
#         user = await UserMod.get(id=userid).only('id', 'deleted_at')
#         user.deleted_at = datetime.now(tz=pytz.UTC)
#         await user.save(update_fields=['deleted_at'])
#         return True
#     except DoesNotExist:
#         raise status.HTTP_404_NOT_FOUND
#
#
# @authrouter.post('/username')
# async def check_username(inst: UniqueFieldsRegistration):
#     exists = await UserMod.filter(username=inst.username).exists()
#     return dict(exists=exists)
#
#
# @authrouter.post('/email')
# async def check_username(inst: UniqueFieldsRegistration):
#     exists = await UserMod.filter(email=inst.email).exists()
#     return dict(exists=exists)
#
#
# @authrouter.get('/readcookie')
# def readcookie(refresh_token: Optional[str] = Cookie(None)):
#     return refresh_token