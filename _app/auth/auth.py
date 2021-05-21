import secrets
from typing import Optional, Union
from tortoise.query_utils import Prefetch
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.user import UserNotExists
from fastapi_users.router.common import ErrorCode
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import generate_jwt
from pydantic import BaseModel, EmailStr, Field, SecretStr, UUID4

from app import ic, red, cache      # noqa
from app.settings import settings as s
from .models import UserMod, User, UserCreate, UserUpdate, UserDB, UserDBComplete
from .models import Group, Permission
from app.auth.models.core import Option
from .Mailman import Mailman
from .FastAPIUsers.JwtAuth import JwtAuth
from .FastAPIUsers.FapiUsers import FapiUsers
from .FastAPIUsers.tortoise import TortoiseUDB



jwtauth = JwtAuth(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
userdb = TortoiseUDB(UserDBComplete, UserMod, include=['username', 'timezone'])
fapiuser = FapiUsers(userdb, [jwtauth], User, UserCreate, UserUpdate, UserDB)
current_user = fapiuser.current_user()
tokenonly = OAuth2PasswordBearer(tokenUrl='token')


async def register_callback(user: UserDB, _: Request):
    """
    Send an email containing a link the user can use to verify their account. This email directly
    shows the success/fail notice upon completion.
    """
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


async def send_registration_email(user: UserMod, text_path: str, html_path: Optional[str] = None,
                                  debug=False):
    debug = debug if s.DEBUG else False
    try:
        user = await fapiuser.get_user(user.email)
    except UserNotExists:
        return
    
    if not user.is_verified and user.is_active:
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            data=token_data,
            secret=s.SECRET_KEY_EMAIL,
            lifetime_seconds=s.VERIFY_EMAIL_TTL,
        )
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


async def send_password_email(user: UserMod, text_path: str, html_path: Optional[str] = None,
                              reset_form_url=None, debug=False):
    debug = debug if s.DEBUG else False
    reset_form_url = reset_form_url or s.FORM_RESET_PASSWORD
    try:
        user = await fapiuser.get_user(user.email)
    except UserNotExists:
        return
    
    if user.is_active and user.is_verified:
        token_data = {
            "user_id": str(user.id),
            "aud": RESET_PASSWORD_TOKEN_AUDIENCE
        }
        token = generate_jwt(
            data=token_data,
            secret=s.SECRET_KEY_EMAIL,
            lifetime_seconds=s.VERIFY_EMAIL_TTL,
        )
        context = {
            'verify_code': token,
            'fake_code': secrets.token_hex(32),
            # 'url': f'{s.SITE_URL}/auth/reset-password?t={token}',
            'url': f'{s.SITE_URL}{reset_form_url}?t={token}',
            'site_name': s.SITE_NAME,
            'title': 'Change Password'
        }
        
        # Prepare the email
        mailman = Mailman(recipient=user.email)
        mailman.setup_email(subject=context['title'])
        mailman.send(text=text_path, html=html_path, context=context)
        
        if debug:
            return context.get('verify_code', None)


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)