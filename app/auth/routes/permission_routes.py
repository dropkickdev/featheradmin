from fastapi import Response, Depends, Body, APIRouter
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import BaseORMException

from app import ic, exceptions as x
from app.auth import current_user
from app.auth.models import Permission
from . import GroupPermissionPy, UserPermissionPy, UpdatePermissionPy, CreatePermissionPy


permrouter = APIRouter()

@permrouter.post('', summary='Create a new Permission', dependencies=[Depends(current_user)])
async def create_permission(res: Response, perm: CreatePermissionPy, user=Depends(current_user)):
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
        raise x.BadError()

# TESTME: Untested
@permrouter.patch('', summary='Rename a Permission')
async def update_permission(res: Response, rel: UpdatePermissionPy, user=Depends(current_user)):
    pass

# TESTME: Untested
@permrouter.delete('', summary='Delete a permission')
async def delete_permission(res: Response, user=Depends(current_user), id: int = Body(...)):
    pass

# TESTME: Untested
@permrouter.patch('/group/attach', summary='Assign a Permission to a Group')
async def assign_grouppermission(res: Response, rel: GroupPermissionPy, user=Depends(current_user)):
    pass

# TESTME: Untested
@permrouter.delete('/group/detach', summary='Remove a Permission from a Group')
async def remove_grouppermission(res: Response, rel: GroupPermissionPy, user=Depends(current_user)):
    pass

# TESTME: Untested
@permrouter.patch('/user/attach', summary='Assign a Permission to a User')
async def assign_userpermission(res: Response, rel: UserPermissionPy, user=Depends(current_user)):
    pass

# TESTME: Untested
@permrouter.delete('/user/detach', summary='Remove a Permission from a User')
async def remove_userpermission(res: Response, rel: UserPermissionPy, user=Depends(current_user)):
    pass

