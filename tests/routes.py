from fastapi import Response, APIRouter, Depends

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