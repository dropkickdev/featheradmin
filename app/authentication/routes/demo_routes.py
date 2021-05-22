from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordBearer

from app.settings import settings as s
from app.auth import current_user

demorouter = APIRouter()



@demorouter.get('/')
async def foo(_: Response):
    return s.TESTDATA


demorouter = APIRouter()
authonly = OAuth2PasswordBearer(tokenUrl='token')

@demorouter.get('/public')
def page_demo(response: Response):
    return 'public'


@demorouter.get('/private', dependencies=[Depends(current_user)])
# async def private(access_token: str = Depends(authonly),
#                   refresh_token: Optional[str] = Cookie(None)):
async def private():
    return 'private'
