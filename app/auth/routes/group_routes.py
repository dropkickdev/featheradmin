from fastapi import Request, Depends, Body, APIRouter, status
from tortoise.exceptions import BaseORMException, DoesNotExist

from app import ic, red
from app.settings import settings as s
from app.auth import current_user, Group
from . import UserGroupPy, CreateGroupPy, UpdateGroupPy



grouprouter = APIRouter()

@grouprouter.post('', summary='Create a new Group', dependencies=[Depends(current_user)],
                  status_code=status.HTTP_201_CREATED)
async def create_group(_: Request, group: CreateGroupPy):
    if not await Group.exists(name=group.name):
        group = await Group.create(**group.dict())
        return {
            'id': group.id,
            'name': group.name,
            'summary': group.summary
        }
    return
    
@grouprouter.patch('', summary='Rename a Group', dependencies=[Depends(current_user)])
async def update_group(_: Request, groupdata: UpdateGroupPy):
    try:
        ll = []
        if not groupdata.name:
            raise ValueError
        
        group = await Group.get_or_none(pk=groupdata.id).only('id', 'name', 'summary')
        if group:
            oldkey = s.CACHE_GROUPNAME.format(group.name)
            newkey = s.CACHE_GROUPNAME.format(groupdata.name)
            ret = await group.update_group(groupdata.name, groupdata.summary)
        
            # Update the cache if exists
            if red.exists(oldkey):
                formatted_oldkey = red.formatkey(oldkey)
                formatted_newkey = red.formatkey(newkey)
                red.rename(formatted_oldkey, formatted_newkey)
            return ret
        return
    except (BaseORMException, ValueError, DoesNotExist):
        return False

# TESTME: Untested
@grouprouter.delete('', summary='Delete a Group')
async def delete_group(_: Request, user=Depends(current_user), id: int = Body(...)):
    pass
