import secrets
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi_users import FastAPIUsers
# from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase
from fastapi_users.user import UserNotExists
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from pydantic import BaseModel, EmailStr, Field, SecretStr

from app import ic
from app.settings import settings as s
from .models import UserMod, User, UserCreate, UserUpdate, UserDB
from app.auth.models.rbac import Group
from .models import HashMod
from .Mailman import Mailman
from .FastAPIUsers.JwtAuth import JwtAuth
from .FastAPIUsers.FapiUsers import FapiUsers


jwtauth = JwtAuth(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
user_db = TortoiseUserDatabase(UserDB, UserMod)
fapiuser = FapiUsers(user_db, [jwtauth], User, UserCreate, UserUpdate, UserDB)      # noqa
current_user = fapiuser.current_user()


def get_verification_token(user: UserDB, token: str, request: Request):
    # return token
    pass


async def register_callback(user: UserDB, request: Request):      # noqa
    # Set the groups for this new user
    groups = await Group.filter(name__in=s.USER_GROUPS)
    user = await UserMod.get(pk=user.id).only('id', 'email')
    await user.groups.add(*groups)
    
    if s.VERIFY_EMAIL:
        await send_registration_email(user,
                                      'app/auth/templates/emails/account/registration_verify_text.jinja2',
                                      'app/auth/templates/emails/account/registration_verify_html.jinja2')


async def user_callback(user: UserDB, updated_fields: dict, request: Request):      # noqa
    pass


async def password_after_reset(user: UserDB, request: Request):
    ic('SUCCESS')


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)


# async def set_verification_code(user, use_type='register'):
#     code = secrets.token_hex(32)
#     await HashMod.create(user=user, hash=code, use_type=use_type)
#     return code


async def send_registration_email(user: UserMod, text_path: str, html_path: Optional[str] = None):
    try:
        user = await fapiuser.get_user(user.email)
    except UserNotExists:
        return
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )
    elif user.is_active:
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(token_data, s.VERIFY_EMAIL_TTL, s.SECRET_KEY)
        context = {
            'verify_code': token,
            'fake_code': secrets.token_hex(32),
            'url': f'{s.SITE_URL}/auth/verify?t={token}',
            'site_name': s.SITE_NAME,
            'title': 'Email Verification'
        }
        
        # Prepare the email
        mailman = Mailman(recipient=user.email)
        mailman.setup_email(subject=context['title'])
        mailman.send(text=text_path, html=html_path, context=context)


async def send_password_email(user: UserMod, text_path: str, html_path: Optional[str] = None):
    
    try:
        user = await fapiuser.get_user(user.email)
    except UserNotExists:
        return
    
    if user.is_active and user.is_verified:
        token_data = {
            "user_id": str(user.id),
            "aud": RESET_PASSWORD_TOKEN_AUDIENCE
        }
        token = generate_jwt(token_data, s.VERIFY_EMAIL_TTL, s.SECRET_KEY_TEMP)
        context = {
            'verify_code': token,
            'fake_code': secrets.token_hex(32),
            'url': f'{s.SITE_URL}/auth/reset-password?t={token}',
            'site_name': s.SITE_NAME,
            'title': 'Change Password'
        }
        
        # Prepare the email
        mailman = Mailman(recipient=user.email)
        mailman.setup_email(subject=context['title'])
        mailman.send(text=text_path, html=html_path, context=context)
        
        return token

# async def send_password_lost_email(user):
#     # data
#     code = await set_verification_code(user)
#     context = {
#         'verify_code': code,
#         'url': f'{s.SITE_URL}/auth/verify/{code}',
#         'site_name': s.SITE_NAME,
#         'title': f'{s.SITE_NAME} Account Verification'
#     }