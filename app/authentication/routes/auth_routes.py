import jwt
from typing import Optional, cast
from fastapi import APIRouter, Response, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM
from fastapi_users.user import UserNotExists, UserAlreadyVerified, UserAlreadyExists
from fastapi_users.password import get_password_hash
from tortoise.exceptions import DoesNotExist
from starlette.responses import RedirectResponse, PlainTextResponse
from pydantic import EmailStr, UUID4

from app.settings import settings as s
from app.auth import (
    userdb, fapiuser, jwtauth, current_user, UserDB,
    REFRESH_TOKEN_KEY, ResetPassword,
    update_refresh_token, create_refresh_token, refresh_cookie, send_password_email
)

authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router())



@authrouter.post("/login")
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends()):
    user = await fapiuser.db.authenticate(credentials)
    
    if user is None or not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    
    try:
        token = await update_refresh_token(user)
    except DoesNotExist:
        token = await create_refresh_token(user)
    
    cookie = refresh_cookie(REFRESH_TOKEN_KEY, token)
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


@authrouter.get("/verify")
async def verify(_: Response, t: Optional[str] = None, debug: bool = False):
    """
    Email verification sent for new registrations then redirect to success/fail notice.
    In the docs this was POST (via react) but I changed it to use GET (via email).
    """
    debug = debug if s.DEBUG else False
    headers = s.NOTICE_HEADER
    
    if not t:
        if debug:
            return False
        return RedirectResponse(url=s.NOTICE_TOKEN_BAD, headers=headers)
    
    try:
        data = jwt.decode(t, s.SECRET_KEY_EMAIL, audience=VERIFY_USER_TOKEN_AUDIENCE,
                          algorithms=[JWT_ALGORITHM])
        user_id = data.get("user_id")
        email = cast(EmailStr, data.get("email"))
        
        if user_id is None:
            if debug:
                return False
            return RedirectResponse(url=s.NOTICE_TOKEN_BAD, headers=headers)
        
        user_check = UserDB(**(await fapiuser.get_user(email)).dict())
        if str(user_check.id) != user_id:
            if debug:
                return False
            return RedirectResponse(url=s.NOTICE_TOKEN_BAD, headers=headers)
        
        # Set is_verified as True
        user = await fapiuser.verify_user(user_check)
        
        if debug:
            return user
        name = user.username or email
        return RedirectResponse(url=f'{s.NOTICE_VERIFY_REGISTER_OK}?name={name}', headers=headers)
    
    except jwt.exceptions.ExpiredSignatureError:
        if debug:
            return False
        return RedirectResponse(url=s.NOTICE_TOKEN_EXPIRED, headers=headers)
    
    except (jwt.PyJWTError, UserNotExists, ValueError):
        if debug:
            return False
        return RedirectResponse(url=s.NOTICE_TOKEN_BAD, headers=headers)
    
    except UserAlreadyVerified:
        if debug:
            return False
        return RedirectResponse(url=s.NOTICE_USER_ALREADY_VERIFIED, headers=headers)


@authrouter.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(_: Response, email: EmailStr = Body(...), debug: bool = Body(False)):
    """Sends an email containing the token to use to access the form to change their password."""
    user = await userdb.get_by_email(email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # TODO: Email must contain the html route NOT the api route
    # TODO: You should queue this with beanstalk or something
    return await send_password_email(
        user,
        'app/authentication/templates/emails/account/password_verify_text.jinja2',
        'app/authentication/templates/emails/account/password_verify_html.jinja2',
        debug=debug
    )


@authrouter.post("/reset-password")
async def reset_password(_: Response, formdata: ResetPassword):
    token = formdata.token
    password = formdata.password
    
    try:
        data = jwt.decode(token, s.SECRET_KEY_EMAIL, audience=RESET_PASSWORD_TOKEN_AUDIENCE,
                          algorithms=[JWT_ALGORITHM])
        user_id = data.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        try:
            user_uuid = UUID4(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        user = await userdb.get(user_uuid)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        
        user.hashed_password = get_password_hash(password)
        # Use UserDB in order to remove the extra attributes generated by UserDBComplete
        user = UserDB(**user.dict())
        await userdb.update(user)
        return True
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )
