from fastapi import Request, Depends, Body, APIRouter
from pydantic import BaseModel

from app.auth import current_user
from . import GroupPermissionPy, UserPermissionPy, UpdatePermissionPy


permrouter = APIRouter()

# PLACEHOLDER: create_permission()
@permrouter.post('/permission', summary='Create a new Permission')
async def create_permission(_: Request, user=Depends(current_user), code=Body(...)):
    pass

# PLACEHOLDER: update_permission()
@permrouter.patch('/permission', summary='Rename a Permission')
async def update_permission(_: Request, rel: UpdatePermissionPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: delete_permission()
@permrouter.delete('/permission', summary='Delete a permission')
async def delete_permission(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# PLACEHOLDER: assign_grouppermission()
@permrouter.post('/permission/group', summary='Assign a Permission to a Group')
async def assign_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: assign_userpermission()
@permrouter.post('/permission/user', summary='Assign a Permission to a User')
async def assign_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_grouppermission()
@permrouter.delete('/permission/group', summary='Remove a Permission from a Group')
async def remove_grouppermission(_: Request, rel: GroupPermissionPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_userpermission()
@permrouter.delete('/permission/user', summary='Remove a Permission from a User')
async def remove_userpermission(_: Request, rel: UserPermissionPy, user=Depends(current_user)):
    pass
