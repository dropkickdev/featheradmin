import smtplib, ssl
from typing import Optional
from fastapi import Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import TortoiseUserDatabase
from pydantic import BaseModel, EmailStr, Field, SecretStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.settings import settings as s
from app import ic
from .models import UserMod, User, UserCreate, UserUpdate, UserDB
from app.auth.models.rbac import Group


jwtauth = JWTAuthentication(secret=s.SECRET_KEY,
                            lifetime_seconds=s.ACCESS_TOKEN_EXPIRE)
user_db = TortoiseUserDatabase(UserDB, UserMod)
fapi_user = FastAPIUsers(user_db, [jwtauth], User, UserCreate, UserUpdate, UserDB)      # noqa



async def register_callback(user: UserDB, request: Request):      # noqa
    groups = await Group.filter(name__in=s.USER_GROUPS)
    user = await UserMod.get(pk=user.id).only('id')
    await user.groups.add(*groups)
    
    # TODO:  Send a confirmation email
    passwd = 'foobar'
    sender = 'aaa@aaa.com'
    recipient = 'bbb@bbb.com'
    text = '''\
Subject: Sup there\n\nThis is a test email. Hello there.
'''
    
    message = MIMEMultipart('alternative')
    message['Subject'] = 'The infamous title on the run'
    message['From'] = sender
    message['To'] = recipient
    html = """\
    <html>
      <body>
        <p>Hi,<br>
           How are you?<br>
           <a href="http://www.realpython.com">Real Python</a>
           has many great tutorials.
        </p>
      </body>
    </html>
    """
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    
    # with smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT) as server:
    #     server.sendmail(sender, recipient, message.as_string())
    smtp_server = None
    try:
        smtp_server = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
        # smtp_server.login(sender, passwd)
        smtp_server.sendmail(sender, recipient, message.as_string())
        smtp_server.quit()
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


async def user_callback(user: UserDB, updated_fields: dict, request: Request):      # noqa
    pass


class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field('', min_length=s.USERNAME_MIN)
    password: SecretStr = Field(..., min_length=s.PASSWORD_MIN)