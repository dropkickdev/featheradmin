import secrets, pytz
from datetime import datetime, timedelta
from fastapi import Response
from fastapi_users import FastAPIUsers
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.user import UserNotExists
from fastapi_users.router.reset import RESET_PASSWORD_TOKEN_AUDIENCE
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import generate_jwt

from .settings import settings as s
from .validation import *
from .authentication.models.manager import *
from .authentication.models.core import *
from .authentication.models.account import *
from .authentication.models.pydantic import *
from .authentication.Mailman import *
from .authentication.FapiUsers import *


userdb = TortoiseUDB(UserDB, UserMod, include=['username', 'timezone'], alternate=UserDBComplete)
jwtauth = JWTAuthentication(secret=s.SECRET_KEY, lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
fapiuser = FastAPIUsers(userdb, [jwtauth], User, UserCreate, UserUpdate, UserDB)

current_user = fapiuser.current_user()
tokenonly = OAuth2PasswordBearer(tokenUrl='token')

REFRESH_TOKEN_KEY = 'refresh_token'         # Don't change this. This is hard-coded as a variable.


async def register_callback(user: UserDB, _: Response):
    """
    Send an email containing a link the user can use to verify their account. This email directly
    shows the success/fail notice upon completion.
    """
    # Set the groups for this new user
    groups = await Group.filter(name__in=s.USER_GROUPS)
    user = await UserMod.get(pk=user.id).only('id', 'email')
    await user.groups.add(*groups)
    
    if s.VERIFY_EMAIL:
        await send_registration_email(
            user,
            'app/authentication/templates/emails/account/registration_verify_text.jinja2',
            'app/authentication/templates/emails/account/registration_verify_html.jinja2'
        )


async def user_callback(user: UserDB, updated_fields: dict, _: Response):
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
            'url': f'{s.SITE_URL}/authentication/verify?t={token}',
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
            # 'url': f'{s.SITE_URL}/authentication/reset-password?t={token}',
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
        raise ValueError('Cookie expires date must be greater than the date now')

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


def time_difference(expires: datetime, now: datetime = None):
    """Get the diff between 2 dates"""
    now = now or datetime.now(tz=pytz.UTC)
    diff = expires - now
    return {
        'days': diff.days,
        'hours': int(diff.total_seconds()) // 3600,
        'minutes': int(diff.total_seconds()) // 60,
        'seconds': int(diff.total_seconds()),
    }


def expires(expires: datetime, units: str = 'minutes'):
    diff = time_difference(expires)
    return diff[units]