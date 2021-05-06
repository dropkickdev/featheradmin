from fastapi import APIRouter, Depends, Response, status, Body, HTTPException
from limeutils import listify

from app import ic
from app.auth import current_user, UserDBComplete, UserMod



accountrouter = APIRouter()

# TODO: Missing permissions
@accountrouter.post('/group', summary='Add group to user', status_code=status.HTTP_201_CREATED)
async def add_group(_: Response, user=Depends(current_user), group: str = Body(...)):
    if not user.has_perm('group.attach'):
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    groups = await usermod.add_group(group)
    return groups

@accountrouter.delete('/group', summary='Remove group from user')
async def remove_group(_: Response, user=Depends(current_user), group: str = Body(...)):
    if not user.has_perm('group.detach'):
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    return await usermod.remove_group(group)

@accountrouter.post('/permission', summary='Add permission to user',
                    status_code=status.HTTP_201_CREATED)
async def add_permission(_: Response, user=Depends(current_user), perms=Body(...)):
    if not user.has_perm('permission.attach'):
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    return await usermod.add_permission(*listify(perms))

@accountrouter.delete('/permission', summary='Remove permission from user')
async def remove_permission(_: Response, user=Depends(current_user), perms=Body(...)):
    if not user.has_perm('permission.detach'):
        return
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    return await usermod.remove_permission(*listify(perms))

@accountrouter.post('/has-perm')
async def has_perm(_: Response, user=Depends(current_user), perms=Body(...)):
    return await user.has_perm(*listify(perms))

