import secrets
from typing import Optional
from fastapi import Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase
from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.settings import settings as s
from .models import UserMod, User, UserCreate, UserUpdate, UserDB
from app.auth.models.rbac import Group
from .models import HashMod
from .Mailman import Mailman


jwtauth = JWTAuthentication(secret=s.SECRET_KEY,
                            lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
user_db = TortoiseUserDatabase(UserDB, UserMod)
fapi_user = FastAPIUsers(user_db, [jwtauth], User, UserCreate, UserUpdate, UserDB)      # noqa



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


async def password_after_forgot(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
    

async def password_after_reset(user: UserDB, request: Request):
    pass


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)


async def set_verification_code(user, use_type='register'):
    code = secrets.token_hex(32)
    await HashMod.create(user=user, hash=code, use_type=use_type)
    return code

async def send_registration_email(user: UserMod, text_path: str, html_path: Optional[str] = None):
    code = await set_verification_code(user)
    context = {
        'verify_code': code,
        'url': f'{s.SITE_URL}/auth/verify/{code}',
        'site_name': s.SITE_NAME,
        'title': f'{s.SITE_NAME} Account Verification'
    }
    
    # Prepare the email
    mailman = Mailman(recipient=user.email)
    mailman.setup_email(subject=f'{s.SITE_NAME} Account Verification')
    mailman.send(text=text_path, html=html_path, context=context)


# async def send_password_lost_email(user):
#     # data
#     code = await set_verification_code(user)
#     context = {
#         'verify_code': code,
#         'url': f'{s.SITE_URL}/auth/verify/{code}',
#         'site_name': s.SITE_NAME,
#         'title': f'{s.SITE_NAME} Account Verification'
#     }