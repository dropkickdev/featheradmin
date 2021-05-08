from fastapi import Request, Depends, Body, APIRouter, status, HTTPException, Response
from tortoise.exceptions import BaseORMException, DoesNotExist

from app import ic, red, exceptions as x
from app.settings import settings as s
from app.auth import current_user, Group
from . import UserGroupPy, CreateGroupPy, UpdateGroupPy, UserMod            # noqa



grouprouter = APIRouter()

@grouprouter.post('', summary='Create a new Group', dependencies=[Depends(current_user)])
async def create_group(res: Response, group: CreateGroupPy, user=Depends(current_user)):
    if not await user.has_perm('group.create'):
        raise x.PermissionDenied()
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    
    if not await Group.exists(name=group.name):
        group = await Group.create(**group.dict())
        res.status_code = 201
        return group.to_dict()

@grouprouter.patch('', summary='Rename a Group', dependencies=[Depends(current_user)])
async def update_group(res: Response, groupdata: UpdateGroupPy, user=Depends(current_user)):
    if not await user.has_perm('group.update'):
        raise x.PermissionDenied()
    try:
        if not groupdata.name:
            raise ValueError('Missing group name to replace existing name')
        
        group = await Group.get_or_none(pk=groupdata.id).only('id', 'name', 'summary')
        if not group:
            raise x.NotFoundError('Group')
        
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

@grouprouter.delete('', summary='Delete a Group')
async def delete_group(res: Response, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.delete'):
        raise x.PermissionDenied()
    if not group:
        raise x.FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    
    group = await Group.get_or_none(name=group.strip()).only('id', 'name')
    if not group:
        raise x.NotFoundError('Group')
    
    partialkey = s.CACHE_GROUPNAME.format(group.name)
    await group.delete()
    red.delete(partialkey)
    res.status_code = 204
    
