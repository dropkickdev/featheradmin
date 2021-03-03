from typing import Optional
from fastapi import APIRouter, Response, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from .settings import settings as s
from .auth.auth import fapiuser, current_user


ACCESS_TOKEN_DEMO = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMWNkZTE2YmItNzA4MS00OGJiLTkxNWEtNTE0ZDI1NzE2ODk5IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjQ2Mjk1NDEzfQ.eDJrBcb9s5K_CjQN2UIvjqd9UusJTNYh_MtoLVDmh1M'

demorouter = APIRouter()
authonly = OAuth2PasswordBearer(tokenUrl='token')

@demorouter.get('/public')
def page_demo(response: Response):
    return 'public'


@demorouter.get('/private', dependencies=[Depends(current_user)])
async def private(access_token: str = Depends(authonly),
                  refresh_token: Optional[str] = Cookie(None)):
    return 'private'
