from typing import Optional
from pydantic import BaseModel, Field


class CreateGroupPy(BaseModel):
    name: str = Field(..., max_length=20)
    summary: str = Field(..., max_length=191)

class UpdateGroupPy(BaseModel):
    id: int
    name: str
    summary: Optional[str] = None


class CreatePermissionPy(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=191)

class UpdatePermissionPy(BaseModel):
    id: int
    code: str = Field(None, max_length=20)
    name: str = Field(None, max_length=191)
    

class UserGroupPy(BaseModel):
    userid: int
    groupid: int

class UserPermissionPy(BaseModel):
    userid: int
    permid: int

class GroupPermissionPy(BaseModel):
    groupid: int
    permid: int
    
    
class ResetPasswordPy(BaseModel):
    token: str
    password: str