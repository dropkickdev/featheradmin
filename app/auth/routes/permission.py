from fastapi import Request, Depends, Body, APIRouter
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import BaseORMException

from app.auth import current_user
from app.auth.models.rbac import Permission
from . import GroupPermissionPy, UserPermissionPy, UpdatePermissionPy, CreatePermissionPy


permrouter = APIRouter()

@permrouter.post('', summary='Create a new Permission', dependencies=[Depends(current_user)])
async def create_permission(_: Request, perm: CreatePermissionPy):
    try:
        perm = await Permission.add(**perm.dict())
        return dict(code=perm.code, name=perm.name)
    except (BaseORMException, ValueError):
        return {}
    

# PLACEHOLDER: update_permission()
@permrouter.patch('', summary='Rename a Permission')
async def update_permission(_: Request, rel: UpdatePermissionPy, user=Depends(current_user)):
    pass


# PLACEHOLDER: delete_permission()
@permrouter.delete('', summary='Delete a permission')
async def delete_permission(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass


# PLACEHOLDER: assign_grouppermission()
@permrouter.post('/group', summary='Assign a Permission to a Group')
async def assign_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass


# PLACEHOLDER: assign_userpermission()
@permrouter.post('/user', summary='Assign a Permission to a User')
async def assign_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass


# PLACEHOLDER: remove_grouppermission()
@permrouter.delete('/group', summary='Remove a Permission from a Group')
async def remove_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass


# PLACEHOLDER: remove_userpermission()
@permrouter.delete('/user', summary='Remove a Permission from a User')
async def remove_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass
