from pickle import loads, dumps
from datetime import datetime
from typing import Optional
from pydantic import UUID4
from fastapi_users.db import TortoiseUserDatabase
from fastapi_users.models import UD
from tortoise.exceptions import DoesNotExist
from tortoise.query_utils import Prefetch

from app import ic, red, cache
from app.auth.models import Group, Option, Permission


class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    starter_fields = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
    
    def __init__(self, *args, include: list = None, usercomplete=None, **kwargs):
        super().__init__(*args, **kwargs)
        include = include or []
        self.usercomplete = usercomplete or self.user_db_model
        self.select_fields = {*self.starter_fields, *include}
    
    async def get(self, id: UUID4) -> Optional[UD]:
        try:
            if user_dict := red.get(f'user-{str(id)}'):
                # ic('CACHE')
                user_dict = cache.restoreuser(user_dict)
            else:
                # ic('CREATE')
                query = self.model.get(id=id)
                
                # Commented for now because of UserDB. No use querying it if it won't be seen.
                # query = query.prefetch_related('groups', 'userpermissions', 'options')
                
                if self.oauth_account_model is not None:
                    query = query.prefetch_related("oauth_accounts")
                    
                user = await query.only(*self.select_fields)
                user_dict = await user.to_dict()
                red.set(f'user-{str(id)}', cache.prepareuser(user_dict), clear=True)
            
            return self.usercomplete(**user_dict)
            
        except DoesNotExist:
            return None