from datetime import datetime
from typing import Optional
from pydantic import UUID4
from fastapi_users.db import TortoiseUserDatabase
from fastapi_users.models import UD
from tortoise.exceptions import DoesNotExist
from tortoise.query_utils import Prefetch

from app import ic
from app.auth.models import Group, Option, Permission


class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    starter_fields = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
    
    def __init__(self, *args, include: list = None, **kwargs):
        super().__init__(*args, **kwargs)
        include = include or []
        self.select_fields = {*self.starter_fields, *include}
        
    def has_cached_user(self, id: UUID4):
        return False
    
    async def get(self, id: UUID4) -> Optional[UD]:
        try:
            # TODO: Check the cache first when using the dependency current_user
            # This gets everything. Cache it.
            query = None
            user = None
            if self.has_cached_user(id):
                pass
            else:
                query = self.model.get(id=id).prefetch_related(
                    'groups', 'userpermissions', 'options'
                )
                if self.oauth_account_model is not None:
                    query = query.prefetch_related("oauth_accounts")
                user = await query.only(*self.select_fields)

            user_dict = await user.to_dict()
            # ic(user_dict)
            return self.user_db_model(**user_dict)
        except DoesNotExist:
            return None