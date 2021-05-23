from typing import Union, Optional, List
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.db import TortoiseBaseUserModel
from tortoise import fields, models
from tortoise.query_utils import Prefetch
from limeutils import modstr, valid_str_only
from tortoise.manager import Manager
from tortoise.exceptions import BaseORMException
from redis.exceptions import RedisError

from app import cache, exceptions as x
from app.settings import settings as s
from app.cache import red
from app.authentication.models.core import DTMixin, Option, SharedMixin
from app.authentication.models.manager import ActiveManager
from app.authentication.pydantic import UpdatePermissionPyd, UpdateGroupPyd



tokenonly = OAuth2PasswordBearer(tokenUrl='token')

class UserMod(DTMixin, TortoiseBaseUserModel):

    
    
        
    
    
    

    

    
    
    
    
    

    
    
    

    

    
    
    


    
    # # TESTME: Untested
    # @classmethod
    # async def is_group(cls, perm: str, group: str):
    #     if not perm or not group:
    #         return False
    #     # Get all the group names from cache
    #     # Save all the groups and perms to cache if they don't exist
    #     # Check the list
    #     # Return the result