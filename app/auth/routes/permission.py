from fastapi import Request, Depends, Body
from pydantic import BaseModel

from app.auth import current_user
from .routes import (
    authrouter,
    GroupPermPy, UserPermPy, PermissionUpdatePy,
)






# PLACEHOLDER: create_permission()
@authrouter.post('/permission', summary='Create a new Permission')
async def create_permission(_: Request, user=Depends(current_user), code=Body(...)):
    pass

# PLACEHOLDER: update_permission()
@authrouter.patch('/permission', summary='Rename a Permission')
async def update_permission(_: Request, rel: PermissionUpdatePy, user=Depends(current_user)):
    pass

# PLACEHOLDER: delete_permission()
@authrouter.delete('/permission', summary='Delete a permission')
async def delete_permission(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# PLACEHOLDER: assign_grouppermission()
@authrouter.post('/permission/group', summary='Assign a Permission to a Group')
async def assign_grouppermission(_: Request, rel: GroupPermPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: assign_userpermission()
@authrouter.post('/permission/user', summary='Assign a Permission to a User')
async def assign_userpermission(_: Request, rel: UserPermPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_grouppermission()
@authrouter.delete('/permission/group', summary='Remove a Permission from a Group')
async def remove_grouppermission(_: Request, rel: GroupPermPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_userpermission()
@authrouter.delete('/permission/user', summary='Remove a Permission from a User')
async def remove_userpermission(_: Request, rel: UserPermPy, user=Depends(current_user)):
    pass
