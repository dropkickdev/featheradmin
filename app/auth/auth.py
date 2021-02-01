import smtplib, ssl, secrets
from typing import Optional
from fastapi import Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase
from pydantic import BaseModel, EmailStr, Field, SecretStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import FileSystemLoader, Environment

from app.settings import settings as s
from app import ic
from .models import UserMod, User, UserCreate, UserUpdate, UserDB
from app.auth.models.rbac import Group, HashMod


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
        await send_verification_email(user,
                                      'app/auth/templates/emails/account/registration_verify_text.jinja2',
                                      'app/auth/templates/emails/account/registration_verify_html.jinja2')


async def user_callback(user: UserDB, updated_fields: dict, request: Request):      # noqa
    pass


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)
    
    
async def send_verification_email(user: UserMod, text_path: str, html_path: Optional[str] = None):
    # data
    code = await set_verification_code(user)
    context = {
        'verify_code': code,
        'url': f'{s.SITE_URL}/auth/verify/{code}',
        'site_name': s.SITE_NAME,
        'title': f'{s.SITE_NAME} Account Verification'
    }
    
    # Prepare the email
    host_user = s.EMAIL_HOST_USER
    host_pass = s.EMAIL_HOST_PASS
    sender = s.EMAIL_SENDER
    recipient = user.email
    message = MIMEMultipart('alternative')
    message['Subject'] = f'{s.SITE_NAME} Account Verification'
    message['From'] = sender
    message['To'] = recipient
    
    # Jinja text
    file_path, file_name = text_path.rsplit('/', 1)
    env = Environment(loader=FileSystemLoader(file_path))
    env.trim_blocks = True
    text_template = env.get_template(file_name)
    text = text_template.render(**context)
    message.attach(MIMEText(text, "plain"))
    
    # Jinja html
    if html_path:
        file_path, file_name = html_path.rsplit('/', 1)
        env = Environment(loader=FileSystemLoader(file_path))
        env.trim_blocks = True
        html_template = env.get_template(file_name)
        html = html_template.render(**context)
        message.attach(MIMEText(html, "html"))
    
    
    # with smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT) as server:
    #     server.sendmail(sender, recipient, message.as_string())
    
    try:
        smtp = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
        # smtp.starttls()
        # smtp.login(host_user, host_pass)
        smtp.sendmail(sender, recipient, message.as_string())
        smtp.quit()
    except Exception as e:
        # TODO: What to do with this
        ic(e)
    
    # server = None
    # context = ssl.create_default_context()
    # try:
    #     server = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
    #     server.starttls(context=context)
    #     server.login(sender, passwd)
    # except Exception as e:
    #     ic(e)
    # finally:
    #     server.quit()
    
    # with smtplib.SMTP_SSL(s.EMAIL_HOST, s.EMAIL_PORT, context=context) as server:
    #     server.login(sender, 'foobar')
    #     server.sendmail(sender, recipient, message)
    
    
async def set_verification_code(user):
    code = secrets.token_hex(32)
    await HashMod.create(user=user, hash=code, use_type='verification')
    return code