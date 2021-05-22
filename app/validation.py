from typing import Optional, Any
from pydantic import BaseModel, Field, validator

from app import ic



class Common:
    @staticmethod
    def not_empty_str(val):
        val = val.strip()
        if not val:
            raise ValueError('Value cannot be empty.')
        return val


class CreatePermission(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    name: str = Field(..., max_length=191)

    @validator('code', 'name')
    def notempty(cls, val):
        return Common.not_empty_str(val)
    

class UpdatePermission(CreatePermission):
    id: int


class CreateGroup(BaseModel):
    name: str = Field(..., max_length=20)
    summary: str = Field('', max_length=191)
    
    @validator('name')
    def notempty(cls, val):
        return Common.not_empty_str(val)


class UpdateGroup(CreateGroup):
    id: int


class UserPermission(BaseModel):
    userid: int
    permid: int


class GroupPermission(BaseModel):
    groupid: int
    permid: int


class ResetPassword(BaseModel):
    token: str
    password: str