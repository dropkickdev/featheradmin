from fastapi import Response, Depends, Body, APIRouter
from tortoise.exceptions import BaseORMException
from redis.exceptions import RedisError

from app import ic, exceptions as x
from app.auth import current_user, Permission, Group, UserMod, UserPermissions
from app.validation import GroupPermission, UserPermission, UpdatePermission, CreatePermission



permrouter = APIRouter()

@permrouter.post('', summary='Create a new Permission')
async def create_permission(res: Response, perm: CreatePermission, user=Depends(current_user)):
    if not await user.has_perm('permission.create'):
        raise x.PermissionDenied()
    if not perm.code:
        raise x.FalsyDataError()
    try:
        perm.name = perm.name or ' '.join(i.capitalize() for i in perm.code.split('.'))
        perm = await Permission.create(**perm.dict())
        res.status_code = 201
        return perm.to_dict()
    except BaseORMException:
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.patch('', summary='Rename a Permission', status_code=204)
async def update_permission(_: Response, perm: UpdatePermission, user=Depends(current_user)):
    if not await user.has_perm('permission.update'):
        raise x.PermissionDenied()
    try:
        await Permission.update_permission(perm)
    except BaseORMException:
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


# TESTME: Untested
@permrouter.delete('', summary='Delete a permission', status_code=204)
async def delete_permission(_: Response, user=Depends(current_user), code: int = Body(...)):
    if not await user.has_perm('permission.delete'):
        raise x.PermissionDenied()
    try:
        if perm := await Permission.get_or_none(code=code).only('id', 'deleted_at'):
            perm.soft_delete()
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


# TESTME: Untested
@permrouter.patch('/group/attach', summary='Attach a Permission to a Group', status_code=204)
async def assign_grouppermission(_: Response, gp: GroupPermission, user=Depends(current_user)):
    if not await user.has_perm('permission.attach'):
        raise x.PermissionDenied()
    try:
        if group := await Group.get_or_none(name=gp.name).only('id'):
            if permlist := await Permission.filter(code__in=gp.codes).only('id'):
                await group.permissions.add(*permlist)
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


# TESTME: Untested
@permrouter.delete('/group/detach', summary='Detach a Permission from a Group', status_code=204)
async def remove_grouppermission(_: Response, gp: GroupPermission, user=Depends(current_user)):
    if not await user.has_perm('permission.detach'):
        raise x.PermissionDenied()
    try:
        if group := await Group.get_or_none(name=gp.name).only('id'):
            if permlist := await Permission.filter(code__in=gp.codes).only('id'):
                await group.permissions.remove(*permlist)
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


# TESTME: Untested
@permrouter.patch('/user/attach', summary='Attach a Permission to a User', status_code=204)
async def assign_userpermission(_: Response, up: UserPermission, user=Depends(current_user)):
    if not await user.has_perm('permission.attach'):
        raise x.PermissionDenied()
    try:
        if usermod := await UserMod.get_or_none(pk=user.id).only('id'):
            if perms := await Permission.filter(code__in=up.codes).only('id'):
                ll = []
                for perm in perms:
                    ll.append(UserPermissions(user=usermod, permission=perm, author=usermod))
                await UserPermissions.bulk_create(ll)
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


# TESTME: Untested
@permrouter.delete('/user/detach', summary='Detach a Permission from a User', status_code=204)
async def remove_userpermission(_: Response, up: UserPermission, user=Depends(current_user)):
    if not await user.has_perm('permission.detach'):
        raise x.PermissionDenied()
    try:
        if perms := await Permission.filter(code__in=up.codes).values_list('id', flat=True):
            if userperms := await UserPermissions.filter(user_id=user.id, permission_id__in=perms):
                for item in userperms:
                    await item.delete()
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()

