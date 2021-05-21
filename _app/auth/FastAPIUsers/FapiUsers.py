from typing import Callable, Optional

from fastapi import APIRouter
from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.fastapi_users import FastAPIUsers
from starlette.requests import Request

# from app.auth.FastAPIUsers.Routers import Routers
# from app.auth.FastAPIUsers.user import get_get_user


REFRESH_TOKEN_KEY = 'refresh_token'
RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"


class FapiUsers(FastAPIUsers):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.get_user = get_get_user(self.db)
