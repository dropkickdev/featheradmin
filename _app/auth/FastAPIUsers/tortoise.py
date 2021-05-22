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




    

    
