from fastapi import Request, Depends, Body, APIRouter
from tortoise.exceptions import BaseORMException

from app import ic
from app.auth import current_user
from app.auth.models.rbac import Group
from . import UserGroupPy, CreateGroupPy, UpdateGroupPy


grouprouter = APIRouter()

@grouprouter.post('', summary='Create a new Group', dependencies=[Depends(current_user)])
async def create_group(_: Request, group: CreateGroupPy):
    try:
        await Group.create(**group.dict())
        return True
    except BaseORMException:
        return False
    

# PLACEHOLDER: update_group()
@grouprouter.patch('', summary='Rename a Group')
async def update_group(_: Request, rel: UpdateGroupPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: delete_group()
@grouprouter.delete('', summary='Delete a Group')
async def delete_group(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass

# PLACEHOLDER: assign_usergroup()
@grouprouter.post('/assign', summary='Assign a Group to a User')
async def assign_grouptouser(_: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass

# PLACEHOLDER: remove_usergroup()
@grouprouter.delete('/remove', summary='Remove a Group from a User')
async def remove_groupfromuser(_: Request, rel: UserGroupPy, user=Depends(current_user)):
    pass