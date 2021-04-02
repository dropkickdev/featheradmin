from fastapi import Request, Depends, Body

from app.auth import current_user
from .routes import authrouter
from .routes import (
    UserGroupPy, UserPermPy,
    GroupPermPy, GroupUpdatePy
)




# TESTME: Untested
@authrouter.post('/group', summary='Create a new Group')
async def create_group(request: Request, user=Depends(current_user), name: int = Body(...)):
    pass

# TESTME: Untested
@authrouter.patch('/group', summary='Rename a Group')
async def update_group(request: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# TESTME: Untested
@authrouter.delete('/group', summary='Delete a Group')
async def delete_group(request: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# TESTME: Untested
@authrouter.post('/group/assign', summary='Assign a Group to a User')
async def assign_usergroup(request: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass

# TESTME: Untested
@authrouter.delete('/group/remove', summary='Remove a Group from a User')
async def remove_usergroup(request: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass