import json
from pydantic import EmailStr
from gettext import gettext as _
from fastapi import Request, HTTPException, status, Body
from tortoise.models import Q

from app.authentication.models.account import UserMod


# TODO: Untested unique_useremail()
async def unique_useremail(request:Request, email: EmailStr = Body(...), username: str = Body(...)):
    exists = await UserMod.exists(Q(username=username) | Q(email=email))
    
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Username and/or email already exists.")
        )
    
    return True


# TODO: Untested unique_username()
async def unique_username(request: Request):
    username = await request.body()
    username = json.loads(username.decode())['username']
    exists = await UserMod.exists(username=username)
    
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Username already exists.")
        )
    
    return True


# TODO: Untested unique_email()
async def unique_email(request: Request):
    email = await request.body()
    email = json.loads(email.decode())['email']
    exists = await UserMod.exists(email=email)

    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Email already exists.")
        )
    
    return True

