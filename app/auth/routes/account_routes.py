from fastapi import APIRouter, Depends, Response, status, Body, HTTPException
from limeutils import listify
from tortoise.exceptions import BaseORMException

from app import ic, UserNotFound, GroupNotFound, PermissionDenied, FalsyDataError
from app.auth import current_user, UserDBComplete, UserMod



accountrouter = APIRouter()

@accountrouter.patch('/group/attach', summary='Add group to user')
async def add_group(res: Response, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.attach'):
        raise PermissionDenied()
    if not group:
        raise FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    
    try:
        if await usermod.add_group(group):
            res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/group/detach', summary='Remove group from user')
async def remove_group(res: Response, user=Depends(current_user), group: str = Body(...)):
    if not await user.has_perm('group.detach'):
        raise PermissionDenied()
    if not group:
        raise FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    
    try:
        await usermod.remove_group(group)
        res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/permission/attach', summary='Add permission to user')
async def add_permission(res: Response, user=Depends(current_user), perms=Body(...)):
    if not await user.has_perm('permission.attach'):
        raise PermissionDenied()
    if not perms:
        raise FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    
    try:
        if await usermod.add_permission(*listify(perms)):
            res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.patch('/permission/detach', summary='Remove permission from user')
async def detach_permission(res: Response, user=Depends(current_user), perms=Body(...)):
    if not await user.has_perm('permission.detach'):
        raise PermissionDenied()
    if not perms:
        raise FalsyDataError()
    
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    if not usermod:
        raise UserNotFound()
    try:
        await usermod.remove_permission(*listify(perms))
        res.status_code = 204
    except BaseORMException:
        pass

@accountrouter.post('/has-perm')
async def has_perm(_: Response, user=Depends(current_user), perms=Body(...), super=Body(True)):
    return await user.has_perm(*listify(perms), superuser=super)

