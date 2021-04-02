from fastapi import Request, Depends, Body

from app.auth import current_user
from .routes import (
    authrouter,
    UserGroupPy, UserPermPy,
    GroupPermPy, GroupUpdatePy
)




# PLACEHOLDER: create_group()
@authrouter.post('/group', summary='Create a new Group')
async def create_group(_: Request, user=Depends(current_user), name: int = Body(...)):
    pass

# PLACEHOLDER: update_group()
@authrouter.patch('/group', summary='Rename a Group')
async def update_group(_: Request, rel: GroupUpdatePy, user=Depends(current_user)):
    pass

# PLACEHOLDER: delete_group()
@authrouter.delete('/group', summary='Delete a Group')
async def delete_group(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# PLACEHOLDER: assign_usergroup()
@authrouter.post('/group/assign', summary='Assign a Group to a User')
async def assign_usergroup(_: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_usergroup()
@authrouter.delete('/group/remove', summary='Remove a Group from a User')
async def remove_usergroup(_: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass