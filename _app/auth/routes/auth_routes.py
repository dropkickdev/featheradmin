import jwt, base64, json, uuid
from typing import Optional, cast
from pydantic import UUID4, EmailStr, ValidationError
from fastapi import Response, Depends, status, Body, Request, Cookie, APIRouter, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi_users.utils import JWT_ALGORITHM
from fastapi_users.user import UserNotExists, UserAlreadyVerified, UserAlreadyExists
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import ErrorCode, run_handler
from starlette.responses import RedirectResponse, PlainTextResponse
from tortoise.exceptions import DoesNotExist

from app import ic      # noqa
from app.authentication import (
    Authcontrol, Authutils, TokenMod,
    jwtauth, userdb, fapiuser, current_user,  # noqa
    register_callback, send_password_email,
    UserDB, TortoiseUDB, UserDBComplete,
)
from app.authentication.routes import ResetPasswordPy
# from app.authentication.FastAPIUsers.tortoise import get_create_user
from app.authentication.models import User, UserCreate
from app.settings import settings as s



# Routes
authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router(register_callback))  # register

# Do not use. Use the customized routes below.
# authrouter.include_router(fapiuser.get_auth_router(jwtauth))    # login, logout
# authrouter.include_router(fapiuser.get_verify_router(s.SECRET_KEY, s.VERIFY_EMAIL_TTL))
# router.include_router(fapi_user.get_users_router(user_callback))
# authrouter.include_router(fapiuser.get_reset_password_router(s.SECRET_KEY_TEMP,
#                                                              after_forgot_password=password_after_forgot,
#                                                              after_reset_password=password_after_reset))

# # DON'T TOUCH THIS. This was placed here and not in settings so it won't be edited.
# REFRESH_TOKEN_KEY = 'refresh_token'



















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