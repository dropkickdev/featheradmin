# from typing import Optional
# from fastapi import APIRouter, Response, Depends, Cookie
# from fastapi.security import OAuth2PasswordBearer
#
# from icecream import ic
# from .settings import settings as s
# from .auth.auth import fapiuser, current_user
#
#
# demorouter = APIRouter()
# authonly = OAuth2PasswordBearer(tokenUrl='token')
#
# @demorouter.get('/public')
# def page_demo(response: Response):
#     return 'public'
#
#
# @demorouter.get('/private', dependencies=[Depends(current_user)])
# # async def private(access_token: str = Depends(authonly),
# #                   refresh_token: Optional[str] = Cookie(None)):
# async def private():
#     return 'private'
