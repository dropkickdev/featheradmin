from fastapi import Response, Depends, Body, APIRouter
from pydantic import Field
from tortoise.exceptions import BaseORMException
from redis.exceptions import RedisError
from limeutils import listify

from app import ic, exceptions as x
from app.auth import current_user, Permission, Group, UserMod, UserPermissions
from app.validation import GroupPermissionVM, UserPermissionVM, UpdatePermissionVM, CreatePermissionVM



permrouter = APIRouter()

@permrouter.post('', summary='Create a new Permission')
async def create_permission(res: Response, perm: CreatePermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.create'):
        raise x.PermissionDenied()
    if not perm.code:
        raise x.FalsyDataError()
    try:
        perm.name = perm.name or ' '.join(i.capitalize() for i in perm.code.split('.'))
        if perm := await Permission.create(**perm.dict()):
            res.status_code = 201
            return perm.to_dict()
    except BaseORMException:
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.patch('', summary='Rename a Permission', status_code=204)
async def update_permission(perm: UpdatePermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.update'):
        raise x.PermissionDenied()
    try:
        await Permission.update_permission(perm)
    except BaseORMException:
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.delete('', summary='Delete a permission')
async def delete_permission(res: Response, code: str = Body(..., min_length=3, max_length=20),
                            user=Depends(current_user)):
    if not await user.has_perm('permission.delete'):
        raise x.PermissionDenied()
    try:
        if perm := await Permission.get_or_none(code=code).only('id', 'deleted_at'):
            # TODO: Update group cache
            # TODO: Find a place to rescan user permissions, maybe on /token?
            await perm.soft_delete()
            res.status_code = 204
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.patch('/attach/group', summary='Attach a Permission to a Group')
async def assign_grouppermission(res: Response, gp: GroupPermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.attach'):
        raise x.PermissionDenied()
    try:
        if group := await Group.get_or_none(name=gp.name).only('id'):
            if permlist := await Permission.filter(code__in=listify(gp.codes)).only('id'):
                await group.permissions.add(*permlist)
                res.status_code = 204
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.delete('/detach/group', summary='Detach a Permission from a Group')
async def remove_grouppermission(res: Response, gp: GroupPermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.detach'):
        raise x.PermissionDenied()
    try:
        if group := await Group.get_or_none(name=gp.name).only('id'):
            if permlist := await Permission.filter(code__in=listify(gp.codes)).only('id'):
                await group.permissions.remove(*permlist)
                res.status_code = 204
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.patch('/attach/user', summary='Attach a Permission to a User')
async def assign_userpermission(res: Response, up: UserPermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.attach'):
        raise x.PermissionDenied()
    try:
        if usermod := await UserMod.get_or_none(pk=user.id).only('id'):
            if codes := list(set(listify(up.codes)) - set(user.permissions)):
                if perms := await Permission.filter(code__in=codes).only('id'):
                    ll = []
                    for perm in perms:
                        ll.append(UserPermissions(user=usermod, permission=perm, author=usermod))
                    await UserPermissions.bulk_create(ll)
                    await UserMod.get_and_cache(user.id)
                    res.status_code = 204
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()


@permrouter.delete('/detach/user', summary='Detach a Permission from a User')
async def remove_userpermission(res: Response, up: UserPermissionVM, user=Depends(current_user)):
    if not await user.has_perm('permission.detach'):
        raise x.PermissionDenied()
    try:
        if perms := await Permission.filter(code__in=listify(up.codes)).values_list('id', flat=True):
            if userperms := await UserPermissions.filter(user_id=user.id, permission_id__in=perms):
                for item in userperms:
                    await item.delete()
                    await UserMod.get_and_cache(user.id)
                    res.status_code = 204
    except (BaseORMException, RedisError):
        raise x.ServiceError()
    except Exception:
        raise x.AppError()

