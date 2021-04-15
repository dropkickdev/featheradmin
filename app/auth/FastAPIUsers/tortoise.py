from pickle import loads, dumps
from datetime import datetime
from typing import Optional, Type, Union
from pydantic import UUID4
from tortoise.query_utils import Prefetch
from fastapi_users import models
from fastapi_users.db import TortoiseUserDatabase, BaseUserDatabase
from fastapi_users.models import UD, BaseUserDB
from tortoise.exceptions import DoesNotExist
from fastapi_users.password import get_password_hash
from fastapi_users.user import UserAlreadyExists, CreateUserProtocol

from app import ic, red, cache
from app.settings import settings as s
from app.auth.models import UserMixin

# # TODO: Update. Still untouched.
# def get_create_user(
#         user_db: BaseUserDatabase[models.BaseUserDB],
#         user_db_model: Type[models.BaseUserDB],
# ) -> CreateUserProtocol:
#     async def create_user(
#             user: models.BaseUserCreate,
#             safe: bool = False,
#             is_active: bool = None,
#             is_verified: bool = None,
#     ) -> models.BaseUserDB:
#         existing_user = await user_db.get_by_email(user.email)
#         # ic(existing_user)
#
#         if existing_user is not None:
#             raise UserAlreadyExists()
#
#         hashed_password = get_password_hash(user.password)
#         user_dict = (
#             user.create_update_dict() if safe else user.create_update_dict_superuser()
#         )
#         db_user = user_db_model(**user_dict, hashed_password=hashed_password)
#         ic(db_user)
#         return await user_db.create(db_user)
#
#     return create_user


class TortoiseUDB(TortoiseUserDatabase):
    # Fields from UserDB
    starter_fields = ['id', 'hashed_password', 'email', 'is_active', 'is_superuser', 'is_verified']
    
    def __init__(self, *args, include: list = None, usercomplete=None, **kwargs):
        include = include or []
        self.select_fields = {*self.starter_fields, *include}
        super().__init__(*args, **kwargs)
        self.usercomplete = usercomplete or self.user_db_model
    
    async def get(self, id: UUID4) -> Optional[UD]:     # noqa
        try:
            partialkey = s.CACHE_USERNAME.format(str(id))
            if user_dict := red.get(partialkey):
                # ic('CACHE')
                user_dict = cache.restoreuser_dict(user_dict)
            else:
                # ic('CREATE')
                query = self.model.get(id=id)
                
                # Commented for now because of UserDB. No use querying it if it won't be seen.
                # query = query.prefetch_related('groups', 'userpermissions', 'options')
                
                if self.oauth_account_model is not None:
                    query = query.prefetch_related("oauth_accounts")
                    
                user = await query.only(*self.select_fields)
                user_dict = await user.to_dict()
                red.set(partialkey, cache.prepareuser(user_dict), clear=True)
            
            return self.usercomplete(**user_dict)
            
        except DoesNotExist:
            return None

    
    # # TODO: Update. Still untouched.
    # async def create(self, user: UD) -> UD:
    #     # ic(user)
    #     user_dict = user.dict()
    #     oauth_accounts = user_dict.pop("oauth_accounts", None)
    #
    #     model = self.model(**user_dict)
    #     await model.save()
    #
    #     if oauth_accounts and self.oauth_account_model:
    #         oauth_account_objects = []
    #         for oauth_account in oauth_accounts:
    #             oauth_account_objects.append(
    #                 self.oauth_account_model(user=model, **oauth_account)
    #             )
    #         await self.oauth_account_model.bulk_create(oauth_account_objects)
    #
    #     return user

    

    
