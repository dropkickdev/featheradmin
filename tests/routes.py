from typing import Optional
from fastapi import Response, APIRouter, Depends, Cookie

from app import exceptions as x
from app.auth import current_user
from app.settings import settings as s


testrouter = APIRouter()

@testrouter.post('/dev_user_data')
async def dev_user_data(_: Response, user=Depends(current_user)):
    return user


@testrouter.get('/open')
async def random_route(_: Response):
    if s.DEBUG:
        raise x.NotFoundError('UserMod')


@testrouter.get('/readcookie')
def readcookie(refresh_token: Optional[str] = Cookie(None)):
    return refresh_token


# @authrouter.post('/username')
# async def check_username(inst: UniqueFieldsRegistration):
#     exists = await UserMod.filter(username=inst.username).exists()
#     return dict(exists=exists)
#
#
# @authrouter.post('/email')
# async def check_username(inst: UniqueFieldsRegistration):
#     exists = await UserMod.filter(email=inst.email).exists()
#     return dict(exists=exists)