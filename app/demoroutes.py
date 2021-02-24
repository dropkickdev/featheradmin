from typing import Optional
from fastapi import APIRouter, Response, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from .settings import settings as s
from .auth.auth import fapiuser


ACCESS_TOKEN_DEMO = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYzZmNzEyNDItZGE4NC00MTY0LWE5NGQtOTZlMDZlMGY4OTI0IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjQ1NzA4NTI5fQ.V968cJj_5M41odgdzm1ZgM-XpxWZ88YDKgiOPdzBE2c'

demorouter = APIRouter()
authonly = OAuth2PasswordBearer(tokenUrl='token')

@demorouter.get('/public')
def page_demo(response: Response):
    return 'public'


@demorouter.get('/private', dependencies=[Depends(fapiuser.get_current_active_user)])
async def private(access_token: str = Depends(authonly),
                  refresh_token: Optional[str] = Cookie(None)):
    return 'private'
