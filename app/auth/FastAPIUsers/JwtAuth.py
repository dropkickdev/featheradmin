import jwt
from pydantic import UUID4
from typing import Any, Optional
from fastapi import Response
from fastapi_users.models import BaseUserDB
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.utils import JWT_ALGORITHM
from fastapi_users.db.base import BaseUserDatabase

from app import ic

class JwtAuth(JWTAuthentication):
    async def __call__(
            self,
            credentials: Optional[str],
            user_db: BaseUserDatabase,
    ) -> Optional[BaseUserDB]:
        if credentials is None:
            return None
        
        try:
            data = jwt.decode(
                credentials,
                self.secret,
                audience=self.token_audience,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None
        
        try:
            user_uiid = UUID4(user_id)
            # ic(type(user_db))
            x = await user_db.get(user_uiid)
            # ic(vars(user_db))
            return x
        except ValueError:
            return None
        
        
    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        """Returned on login"""
        token = await self._generate_token(user)
        return {"access_token": token, "token_type": "bearer", 'is_verified': user.is_verified}