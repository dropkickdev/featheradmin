from typing import Optional
from fastapi_users.db import TortoiseUserDatabase
from fastapi_users.models import UD
from pydantic import UUID4

from app import red, ic, cache
from app.settings import settings as s



class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    starter_fields = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
    
    def __init__(self, *args, include: Optional[list] = None, alternate=None, **kwargs):
        include = include or []
        self.select_fields = {*self.starter_fields, *include}
        super().__init__(*args, **kwargs)
        self.usercomplete = alternate or self.user_db_model
    
    async def get(self, id: UUID4) -> Optional[UD]:     # noqa
        partialkey = s.CACHE_USERNAME.format(str(id))
        if user_dict := red.get(partialkey):
            # ic('CACHE')
            user_dict = cache.restoreuser_dict(user_dict)
        else:
            # ic('CREATE')
            query = self.model.get_or_none(id=id)
            
            # No use querying this if it won't be seen
            # query = query.prefetch_related('groups', 'userpermissions', 'options')

            if self.oauth_account_model is not None:
                query = query.prefetch_related("oauth_accounts")
            
            usermod = await query.only(*self.select_fields)
            if not usermod:
                return
            user_dict = await usermod.to_dict()
            red.set(partialkey, cache.prepareuser_dict(user_dict), clear=True)
            
            # pydantic_user = await cast(
            #     PydanticModel, self.user_db_model
            # ).from_tortoise_orm(usermod)
            # return cast(UD, pydantic_user)
            
        return self.usercomplete(**user_dict)
