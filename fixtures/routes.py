from fastapi import APIRouter
from tortoise import transactions

from app.auth.models.rbac import Group, Permission, GroupPermissions

fixturerouter = APIRouter()


@fixturerouter.get('/init')
async def fixtures():
    try:
        async with transactions.in_transaction():
            # Data sections
            data_list = ['page', 'book']
            
            # Groups
            groups = []
            for group in ['AdminGroup', 'StaffGroup',
                          'AccountGroup', 'DataGroup', 'ProfileGroup',  # Default groups
                          'StrictDataGroup']:
                groups.append(Group(name=group))
            await Group.bulk_create(groups)
            
            # Permissions
            permissions = []
            permissions.extend([
                Permission(name=f'Ban user', code=f'auth.ban'),
                Permission(name=f'Unban user', code=f'auth.unban'),
                Permission(name=f'Reset password counter', code=f'auth.reset_password_counter'),
            ])
            for i in ['user', 'settings', 'profile'] + data_list:
                permissions.extend([
                    Permission(name=f'{i.capitalize()} Create', code=f'{i.lower()}.create'),
                    Permission(name=f'{i.capitalize()} Read', code=f'{i.lower()}.read'),
                    Permission(name=f'{i.capitalize()} Update', code=f'{i.lower()}.update'),
                    Permission(name=f'{i.capitalize()} Delete', code=f'{i.lower()}.delete'),
                    Permission(name=f'{i.capitalize()} Hard Delete', code=f'{i.lower()}.hard_delete'),
                ])
            await Permission.bulk_create(permissions)
            
            # Group Permissions
            groups = dict(await Group.all().values_list('name', 'id'))
            perms = dict(await Permission.all().values_list('code', 'id'))
            
            groupperms = []
            for code in perms.keys():
                app, action = code.split('.')
    
    
                if app == 'user':
                    if action == 'create':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AdminGroup'], permission_id=perms[code]),
                        ])
                    elif action == 'delete':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AdminGroup'], permission_id=perms[code]),
                        ])
                    elif action == 'hard_delete':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AdminGroup'], permission_id=perms[code]),
                        ])
                
                if app == 'settings':
                    if action == 'read':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AccountGroup'],
                                             permission_id=perms[code]),
                        ])
                    elif action == 'update':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AccountGroup'],
                                             permission_id=perms[code]),
                        ])
    
                if app == 'profile':
                    if action == 'read':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['ProfileGroup'],
                                             permission_id=perms[code]),
                        ])
                    elif action == 'update':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['ProfileGroup'],
                                             permission_id=perms[code]),
                        ])
                
                elif app in data_list:
                    if action == 'create':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['DataGroup'], permission_id=perms[code]),
                        ])
                    elif action == 'read':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['DataGroup'], permission_id=perms[code]),
                            GroupPermissions(group_id=groups['StrictDataGroup'],
                                             permission_id=perms[code]),
                        ])
                    elif action == 'update':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['DataGroup'], permission_id=perms[code]),
                        ])
                    elif action == 'delete':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['DataGroup'], permission_id=perms[code]),
                        ])
                    elif action == 'hard_delete':
                        groupperms.extend([
                            GroupPermissions(group_id=groups['AdminGroup'], permission_id=perms[code]),
                            GroupPermissions(group_id=groups['StaffGroup'], permission_id=perms[code]),
                        ])
            groupperms.extend([
                GroupPermissions(group_id=groups['AdminGroup'], permission_id=1),
                GroupPermissions(group_id=groups['AdminGroup'], permission_id=2),
                GroupPermissions(group_id=groups['AdminGroup'], permission_id=3),
                GroupPermissions(group_id=groups['StaffGroup'], permission_id=1),
                GroupPermissions(group_id=groups['StaffGroup'], permission_id=2),
                GroupPermissions(group_id=groups['StaffGroup'], permission_id=3),
            ])
            await GroupPermissions.bulk_create(groupperms)
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
