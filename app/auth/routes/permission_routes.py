from fastapi import Request, Depends, Body, APIRouter
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import BaseORMException

from app import ic
from app.auth import current_user
from app.auth.models import Permission
from . import GroupPermissionPy, UserPermissionPy, UpdatePermissionPy, CreatePermissionPy


permrouter = APIRouter()

@permrouter.post('', summary='Create a new Permission', dependencies=[Depends(current_user)])
async def create_permission(_: Request, perm: CreatePermissionPy):
    try:
        perm = await Permission.add(**perm.dict())
        return dict(code=perm.code, name=perm.name)
    except (BaseORMException, ValueError):
        return {}


# TESTME: Untested
@permrouter.patch('', summary='Rename a Permission')
async def update_permission(_: Request, rel: UpdatePermissionPy, user=Depends(current_user)):
    pass


# TESTME: Untested
@permrouter.delete('', summary='Delete a permission')
async def delete_permission(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass


# TESTME: Untested
@permrouter.post('/group', summary='Assign a Permission to a Group')
async def assign_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass


# TESTME: Untested
@permrouter.post('/user', summary='Assign a Permission to a User')
async def assign_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass


# TESTME: Untested
@permrouter.delete('/group', summary='Remove a Permission from a Group')
async def remove_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass


# TESTME: Untested
@permrouter.delete('/user', summary='Remove a Permission from a User')
async def remove_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass
