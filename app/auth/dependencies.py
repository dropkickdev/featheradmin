import json
from fastapi import Request

from .models.user import UserMod
from .exceptions import XUSERNAME_EXISTS, XEMAIL_EXISTS



async def unique_username(request: Request):
    username = await request.body()
    username = json.loads(username.decode())['username']
    exists = await UserMod.exists(username=username)
    if exists:
        raise XUSERNAME_EXISTS
    return True


async def unique_email(request: Request):
    email = await request.body()
    email = json.loads(email.decode())['email']
    exists = await UserMod.exists(email=email)
    if exists:
        raise XEMAIL_EXISTS
    return True

