import json
from gettext import gettext as _
from fastapi import Request, HTTPException, status

from app.auth.models.user import UserMod



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

