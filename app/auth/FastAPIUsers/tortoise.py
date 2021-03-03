from typing import Optional
from pydantic import UUID4
from fastapi_users.db import TortoiseUserDatabase
from fastapi_users.models import UD
from tortoise.exceptions import DoesNotExist

from app import ic


class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    current_user_fields = []
    
    def has_cached_user(self, id: UUID4 = None):
        return False
    
    async def get(self, id: UUID4) -> Optional[UD]:
        try:
            # TODO: Check the cache first when using the dependency current_user
            # This gets everything. Cache it.
            query = None
            if self.has_cached_user():
                # You can probably use the walrus op for this
                pass
            else:
                query = self.model.get(id=id)

            if self.oauth_account_model is not None:
                query = query.prefetch_related("oauth_accounts")

            user = await query
            ic(type(user), vars(user))
            user_dict = await user.to_dict()
            ic(user_dict)

            x = self.user_db_model(**user_dict)
            ic(x)
            return x
        except DoesNotExist:
            return None