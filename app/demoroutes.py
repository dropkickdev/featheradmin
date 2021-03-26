from typing import Optional
from fastapi import APIRouter, Response, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from .settings import settings as s
from .auth.auth import fapiuser, current_user


ACCESS_TOKEN_DEMO = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMmNhMzYxNWEtNTE2Yi00NWI1LWEzNGItZjdmZDU3YTZlMmI3IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjQ4MjgyMTM4fQ.cd-USTJbR-aZ9xTmQmTQFl8Qd48zk9KeFZRsF3uw57g'

demorouter = APIRouter()
authonly = OAuth2PasswordBearer(tokenUrl='token')

@demorouter.get('/public')
def page_demo(response: Response):
    return 'public'


@demorouter.get('/private', dependencies=[Depends(current_user)])
async def private(access_token: str = Depends(authonly),
                  refresh_token: Optional[str] = Cookie(None)):
    return 'private'
