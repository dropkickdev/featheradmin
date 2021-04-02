from fastapi import APIRouter
from pydantic import BaseModel, Field



authrouter = APIRouter()


class GroupUpdatePy(BaseModel):
    groupid: int
    name: str


class UserGroupPy(BaseModel):
    user: int
    group: int


class UserPermPy(BaseModel):
    user: int
    perm: int


class GroupPermPy(BaseModel):
    group: int
    perm: int