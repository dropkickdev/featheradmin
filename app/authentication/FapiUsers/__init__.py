from typing import cast, Optional
from fastapi_users.db import TortoiseUserDatabase, BaseUserDatabase
from fastapi_users.models import UD
from tortoise.exceptions import DoesNotExist
from tortoise.contrib.pydantic import PydanticModel
from pydantic import UUID4

from app import red, ic, cache
from app.settings import settings as s



class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    starter_fields = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
    
    def __init__(self, *args, include: list = None, usercomplete=None, **kwargs):
        include = include or []
        self.select_fields = {*self.starter_fields, *include}
        super().__init__(*args, **kwargs)
        self.usercomplete = usercomplete or self.user_db_model
    
    async def get(self, id: UUID4) -> Optional[UD]:     # noqa
        partialkey = s.CACHE_USERNAME.format(str(id))
        if user_dict := red.get(partialkey):
            # ic('CACHE')
            user_dict = cache.restoreuser_dict(user_dict)
            return self.usercomplete(**user_dict)
        else:
            # ic('CREATE')
            try:
                query = self.model.get(id=id)
                
                # Commented for now because of UserDB. No use querying it if it won't be seen.
                # query = query.prefetch_related('groups', 'userpermissions', 'options')
    
                if self.oauth_account_model is not None:
                    query = query.prefetch_related("oauth_accounts")
                
                usermod = await query.only(*self.select_fields)
                pydantic_user = await cast(
                    PydanticModel, self.user_db_model
                ).from_tortoise_orm(usermod)
                user_dict = await usermod.to_dict()
                
                # Cache
                red.set(partialkey, cache.prepareuser_dict(user_dict), clear=True)
                
                # Permission data
                # perms = await usermod.get_permissions()
                
                return cast(UD, pydantic_user)
            except DoesNotExist:
                return