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
userdb = TortoiseUDB(UserDBComplete, UserMod, include=['username', 'timezone'],
                     group=Group, permission=Permission, option=Option)
fapiuser = FapiUsers(userdb, [jwtauth], User, UserCreate, UserUpdate, UserDB)
current_user = fapiuser.current_user()
tokenonly = OAuth2PasswordBearer(tokenUrl='token')


async def register_callback(user: UserDB, _: Request):
    # ic(type(user), user)
    # user_dict = user.dict()
    # user_dict['id'] = str(user_dict['id'])
    # user_dict['is_active'] = str(user_dict['is_active'])
    # user_dict['is_verified'] = str(user_dict['is_verified'])
    # user_dict['is_superuser'] = str(user_dict['is_superuser'])
    # redconn.conn.hset(str(user.id), mapping=user_dict)
    
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
        token = generate_jwt(
            data=token_data,
            secret=s.SECRET_KEY_TEMP,
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
        token = generate_jwt(
            data=token_data,
            secret=s.SECRET_KEY_TEMP,
            lifetime_seconds=s.VERIFY_EMAIL_TTL,
        )
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


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)


# async def user_data(id: str, save_cache=False) -> UserDBComplete:
#     """
#     Returns same data as the current_user dependency. Patterned from TortoiseUDB get() method.
#     Returns simple user data to be saved to cache. Does not include: options and groups
#     :param id:          User id to use
#     :param save_cache:  Replace the user data in the cache
#     :return:            UserDBComplete
#     """
#     id = isinstance(id, str) and id or str(id)
#     partialkey = s.CACHE_USERNAME.format(id)
#     if False:
#         pass
#     # if user_dict := red.get(partialkey):
#     #     user_dict = cache.restoreuser(user_dict)
#     else:
#         user_dict = await UserMod.get_and_cache(id)
#         # user = await UserMod.get_or_none(pk=id) \
#         #     .prefetch_related(
#         #     Prefetch('groups', queryset=Group.filter(deleted_at=None).only('id', 'name')),
#         #     Prefetch('options', queryset=Option.filter(is_active=True)
#         #              .only('user_id', 'name', 'value')),
#         #     # Prefetch('permissions', queryset=Permission.filter(deleted_at=None).only('id', 'code'))
#         # ).only(*userdb.select_fields)
#         #
#         # if user:
#         #     user_dict = await user.to_dict()
#         #     red.set(partialkey, cache.prepareuser(user_dict), clear=True)
#
#         # user_dict = await UserMod.get_and_cache(id)
#     #     query = UserMod.get(id=id)
#     #
#     #     if userdb.oauth_account_model is not None:
#     #         query = query.prefetch_related("oauth_accounts")
#     #
#     #     user = await query.only(*userdb.select_fields)
#     #     user_dict = await user.to_dict()
#     #
#     #     if save_cache:
#     #         red.set(s.CACHE_USERNAME.format(id), cache.prepareuser(user_dict), clear=True)
#     return UserDBComplete(**user_dict)