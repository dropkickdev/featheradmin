from fastapi import Request, Depends, Body, APIRouter
from tortoise.exceptions import BaseORMException, DoesNotExist

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
    

@grouprouter.patch('', summary='Rename a Group', dependencies=[Depends(current_user)])
async def update_group(_: Request, groupdata: UpdateGroupPy):
    try:
        ll = []
        if not groupdata.name:
            raise ValueError
        
        group = await Group.get(id=groupdata.id).only('id', 'name', 'summary')
        if group.name != groupdata.name:
            ll.append('name')
            group.name = groupdata.name.strip()
        if group.summary != groupdata.summary:
            ll.append('summary')
            group.summary = groupdata.summary.strip()
        if ll:
            await group.save(update_fields=ll)
        return True
    except (BaseORMException, ValueError, DoesNotExist):
        return False

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