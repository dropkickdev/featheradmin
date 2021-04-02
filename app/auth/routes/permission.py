from fastapi import Request, Depends, Body
from pydantic import BaseModel

from app.auth import current_user
from .routes import authrouter






# TESTME: Untested
@authrouter.post('/create-permission', summary='Create a new Permission')
async def create_permission(request: Request, user=Depends(current_user), perm=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/update-permission', summary='Rename a Permission')
async def update_permission(request: Request, user=Depends(current_user), permid=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/delete-permission', summary='Delete a permission')
async def delete_permission(request: Request, user=Depends(current_user), permid=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/assign-grouppermission', summary='Assign a Permission to a Group')
async def assign_grouppermission(request: Request, user=Depends(current_user),
                                 permid=Body(...), groupid=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/assign-userpermission', summary='Assign a Permission to a User')
async def assign_userpermission(request: Request, user=Depends(current_user),
                                permid=Body(...), userid=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/remove-grouppermission', summary='Remove a Permission from a Group')
async def remove_grouppermission(request: Request, user=Depends(current_user),
                                 permid=Body(...), groupid=Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/remove-userpermission', summary='Remove a Permission from a User')
async def remove_userpermission(request: Request, user=Depends(current_user),
                                permid=Body(...), userid=Body(...)):
    pass