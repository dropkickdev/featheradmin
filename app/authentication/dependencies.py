from pydantic import EmailStr
from fastapi import Request, Body
from tortoise.models import Q

from app import exceptions as x
from app.auth import UserMod


# TESTME: Untested
async def unique_account(_:Request, email: EmailStr = Body(...), username: str = Body(...)):
    if await UserMod.exists(Q(username=username) | Q(email=email)):
        raise x.UnusableDataError('ACCOUNT ALREADY EXISTS')
    return True
