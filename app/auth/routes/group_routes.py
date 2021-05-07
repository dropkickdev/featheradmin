from fastapi import Request, Depends, Body, APIRouter, status, HTTPException
from tortoise.exceptions import BaseORMException, DoesNotExist

from app import ic, red
from app.settings import settings as s
from app.auth import current_user, Group
from . import UserGroupPy, CreateGroupPy, UpdateGroupPy, UserMod



grouprouter = APIRouter()

@grouprouter.post('', summary='Create a new Group', dependencies=[Depends(current_user)],
                  status_code=201)
async def create_group(res: Request, group: CreateGroupPy, user=Depends(current_user)):
    if not await user.has_perm('group.create'):
        res.status_code = 403
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        return
    
    if not await Group.exists(name=group.name):
        group = await Group.create(**group.dict())
        return {
            'id': group.id,                                                     # noqa
            'name': group.name,
            'summary': group.summary
    }

@grouprouter.patch('', summary='Rename a Group', dependencies=[Depends(current_user)])
async def update_group(res: Request, groupdata: UpdateGroupPy, user=Depends(current_user)):
    if not await user.has_perm('group.update'):
        res.status_code = 403
        return
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

@grouprouter.delete('', summary='Delete a Group')
async def delete_group(res: Request, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.delete'):
        res.status_code = 403
        return
    if not group:
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        return
    
    # if not await usermod.has_perm('group.delete', super=user.is_superuser):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    group = await Group.get_or_none(name=group.strip()).only('id', 'name')
    if group:
        partialkey = s.CACHE_GROUPNAME.format(group.name)
        await group.delete()
        red.delete(partialkey)
    return
    
    
