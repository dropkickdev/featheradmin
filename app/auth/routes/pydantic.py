from pydantic import BaseModel, Field


class CreateGroupPy(BaseModel):
    name: str = Field(..., max_length=20)
    summary: str = Field(..., max_length=199)

class UpdateGroupPy(BaseModel):
    id: int
    name: str


class CreatePermissionPy(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=199)

class UpdatePermissionPy(BaseModel):
    id: int
    code: str
    

class UserGroupPy(BaseModel):
    userid: int
    groupid: int

class UserPermissionPy(BaseModel):
    userid: int
    permid: int

class GroupPermissionPy(BaseModel):
    groupid: int
    permid: int