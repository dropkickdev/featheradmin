from fastapi import APIRouter
from pydantic import BaseModel, Field



authrouter = APIRouter()


class GroupUpdatePy(BaseModel):
    id: int
    name: str
    
    
class PermissionUpdatePy(BaseModel):
    id: int
    code: str
    

class UserGroupPy(BaseModel):
    userid: int
    groupid: int


class UserPermPy(BaseModel):
    userid: int
    permid: int


class GroupPermPy(BaseModel):
    groupid: int
    permid: int