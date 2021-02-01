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
    print(vars(user))
    await user.groups.add(*groups)
    
    if s.VERIFY_EMAIL:
        code = 'def456'
        await send_verification_email(
            user=user,
            verify_code=code,
            template_path='app/auth/templates/emails/account/registration_verify.html'
        )


async def user_callback(user: UserDB, updated_fields: dict, request: Request):      # noqa
    pass


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)
    
    
async def send_verification_email(*, user: UserMod, verify_code: str, template_path: str):
    file_path, file_name = template_path.rsplit('/', 1)
    
    # Jinja
    env = Environment(loader=FileSystemLoader(file_path))
    env.trim_blocks = True
    template = env.get_template(file_name)
    
    verify_code = await set_verification_code(user)
    html = template.render(verify_code=verify_code)
    
    # TODO:  Send a confirmation email
    # Send the email
    passwd = 'foobar'
    sender = s.EMAIL_SENDER
    recipient = user.email
    text = '''\
    Subject: Sup there\n\nThis is a test email. Hello there.
    '''
    
    message = MIMEMultipart('alternative')
    message['Subject'] = 'The infamous title on the run'
    message['From'] = sender
    message['To'] = recipient
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    
    # with smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT) as server:
    #     server.sendmail(sender, recipient, message.as_string())
    
    try:
        smtp = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
        # smtp_server.login(sender, passwd)
        smtp.sendmail(sender, recipient, message.as_string())
        smtp.quit()
    except Exception as e:
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