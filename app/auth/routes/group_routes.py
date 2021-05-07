from fastapi import Request, Depends, Body, APIRouter, status, HTTPException
from tortoise.exceptions import BaseORMException, DoesNotExist

from app import ic, red, PermissionDenied, UserNotFound, GroupNotFound, FalseyDataError
from app.settings import settings as s
from app.auth import current_user, Group
from . import UserGroupPy, CreateGroupPy, UpdateGroupPy, UserMod



grouprouter = APIRouter()

@grouprouter.post('', summary='Create a new Group', dependencies=[Depends(current_user)],
                  status_code=201)
async def create_group(res: Request, group: CreateGroupPy, user=Depends(current_user)):
    if not await user.has_perm('group.create'):
        raise PermissionDenied()
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    
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
        raise PermissionDenied()
    try:
        if not groupdata.name:
            raise ValueError('Missing group name to replace existing name')
        
        group = await Group.get_or_none(pk=groupdata.id).only('id', 'name', 'summary')
        if not group:
            raise GroupNotFound()
        
        oldkey = s.CACHE_GROUPNAME.format(group.name)
        newkey = s.CACHE_GROUPNAME.format(groupdata.name)
        await group.update_group(groupdata.name, groupdata.summary)
        res.status_code = 204
    
        # Update the cache if exists
        if red.exists(oldkey):
            formatted_oldkey = red.formatkey(oldkey)
            formatted_newkey = red.formatkey(newkey)
            red.rename(formatted_oldkey, formatted_newkey)
    except (BaseORMException, ValueError, DoesNotExist):
        return

@grouprouter.delete('', summary='Delete a Group', status_code=204)
async def delete_group(_: Request, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.delete'):
        raise PermissionDenied()
    if not group:
        raise FalseyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    
    group = await Group.get_or_none(name=group.strip()).only('id', 'name')
    if not group:
        raise GroupNotFound()
    
    partialkey = s.CACHE_GROUPNAME.format(group.name)
    await group.delete()
    red.delete(partialkey)
    
