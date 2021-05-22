from fastapi import APIRouter, Depends, Response, Body
from limeutils import listify
from tortoise.exceptions import BaseORMException

from app import ic, exceptions as x
from app.auth import current_user, UserMod



accountrouter = APIRouter()

@accountrouter.patch('/group/attach', summary='Add group to user')
async def add_group(res: Response, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.attach'):
        raise x.PermissionDenied()
    if not group:
        raise x.FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    
    try:
        if await usermod.add_group(group):
            res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/group/detach', summary='Remove group from user')
async def remove_group(res: Response, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.detach'):
        raise x.PermissionDenied()
    if not group:
        raise x.FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    
    try:
        await usermod.remove_group(group)
        res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/permission/attach', summary='Add permission to user')
async def add_permission(res: Response, user=Depends(current_user), perms=Body(...)):
    if not await user.has_perm('permission.attach'):
        raise x.PermissionDenied()
    if not perms:
        raise x.FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    
    try:
        if await usermod.add_permission(*listify(perms)):
            res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/permission/detach', summary='Remove permission from user')
async def detach_permission(res: Response, user=Depends(current_user), perms=Body(...)):
    if not await user.has_perm('permission.detach'):
        raise x.PermissionDenied()
    if not perms:
        raise x.FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise x.NotFoundError('User')
    try:
        await usermod.remove_permission(*listify(perms))
        res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.post('/has-perm')
async def has_perm(_: Response, user=Depends(current_user), perms=Body(...), superuser=Body(True)):
    return await user.has_perm(*listify(perms), superuser=superuser)

