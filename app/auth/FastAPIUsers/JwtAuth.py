from abc import ABC
from typing import Any
from fastapi import Response
from fastapi_users.models import BaseUserDB
from fastapi_users.authentication import JWTAuthentication

from app import ic

class JwtAuth(ABC, JWTAuthentication):
    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        """Returned on login"""
        token = await self._generate_token(user)
        return {"access_token": token, "token_type": "bearer", 'is_verified': user.is_verified}