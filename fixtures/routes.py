import json, time
from fastapi import APIRouter
from tortoise import transactions

from app.auth.models.rbac import Group, Permission
from app.auth.models.core import Option
from tests.auth_test import VERIFIED_USER_DEMO



fixturerouter = APIRouter()
data_list = ['page', 'book']


# @fixturerouter.get('/init')
# async def fixtures():
#     try:
#         async with transactions.in_transaction():
#             # Groups
#             groups = []
#             for group in ['AdminGroup', 'StaffGroup',
#                           'AccountGroup', 'DataGroup',  # Default groups
#                           'StrictdataGroup']:
#                 groups.append(Group(name=group))
#             await Group.bulk_create(groups)
#
#             # Permissions
#             permissions = []
#             permissions.extend([
#                 Permission(name=f'Ban user', code=f'auth.ban'),
#                 Permission(name=f'Unban user', code=f'auth.unban'),
#                 Permission(name=f'Reset password counter', code=f'auth.reset_password_counter'),
#             ])
#             for i in ['user', 'settings', 'profile'] + data_list:
#                 permissions.extend([
#                     Permission(name=f'{i.capitalize()} Create', code=f'{i.lower()}.create'),
#                     Permission(name=f'{i.capitalize()} Read', code=f'{i.lower()}.read'),
#                     Permission(name=f'{i.capitalize()} Update', code=f'{i.lower()}.update'),
#                     Permission(name=f'{i.capitalize()} Delete', code=f'{i.lower()}.delete'),
#                     Permission(name=f'{i.capitalize()} Hard Delete', code=f'{i.lower()}.hard_delete'),
#                 ])
#             await Permission.bulk_create(permissions)
#
#             # Group permissions
#             await group_permissions(data_list)
#
#             # Create your first user here and populate VERIFIED_USER_ID
#
#             return True
#     except Exception:
#         return False

perms = {
    'DataGroup': {
        'page': ['create', 'read', 'update', 'delete'],
        'book': ['create', 'read', 'update', 'delete'],
    },
    'AccountGroup': {
        'profile': ['read', 'update'],
        'setting': ['read', 'update'],
    },
    'AdminGroup': {
        'user': ['create', 'delete', 'hard_delete'],
        'auth': ['ban', 'unban', 'reset_password_counter'],
    },
    'StaffGroup': {
        'auth': ['ban', 'unban', 'reset_password_counter'],
    },
}

@fixturerouter.get('/init')
async def group_permissions():
    for groupname, val in perms.items():
        group = await Group.create(name=groupname)
        for app, actions in val.items():
            for i in actions:
                await Permission.create(
                    name=f'{app.capitalize()} {i.capitalize()}', code=f'{app}.{i}'
                )


@fixturerouter.get('/group_permissions')
async def group_permissions_through():
    for groupname, val in perms.items():
        group = await Group.get(name=groupname).only('id')
        ll = []
        for app, actions in val.items():
            for i in actions:
                ll.append(f'{app}.{i}')
        permlist = await Permission.filter(code__in=ll).only('id')
        await group.permissions.add(*permlist)


@fixturerouter.get('/options')
async def options():
    try:
        await Option.create(name='sitename', value='Feather Admin')
        await Option.create(name='author', value='DropkickDev')
        await Option.create(name='cool', value='yo', user_id=VERIFIED_USER_DEMO)
        await Option.create(name='theme', value='purple', user_id=VERIFIED_USER_DEMO)
        return True
    except Exception:
        return False
    
# @router.get('/testing')
# async def testing():
#     try:
#         # rtoken = await Token.filter(id__in=[1,2]).update(is_blacklisted=False)
#         rtoken = await Token.get(id=1).only('id')
#         rtoken.is_blacklisted=True
#         await rtoken.save(update_fields=['is_blacklisted'])
#         return rtoken
#     except DoesNotExist:
#         return False

