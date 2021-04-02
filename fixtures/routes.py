from fastapi import APIRouter, HTTPException, status, FastAPI
from fastapi_users.user import get_create_user
from fastapi_users.user import UserAlreadyExists
from fastapi_users.router.common import ErrorCode
from pydantic import EmailStr

from app import red
from app.settings import settings as s
from app.auth import userdb, UserDB, UserCreate, UserMod
from app.auth.models.rbac import Group, Permission, UserPermissions
from app.auth.models.core import Option
from tests.auth_test import VERIFIED_USER_DEMO
from fixtures.permissions import DataGroup, AccountGroup, StaffGroup, AdminGroup



app = FastAPI()
fixturerouter = APIRouter()

perms = {
    'DataGroup': DataGroup,
    'AccountGroup': AccountGroup,
    'StaffGroup': StaffGroup,
    'AdminGroup': AdminGroup,
    'NoaddGroup': {
        'foo': ['read', 'update', 'delete', 'hard_delete'],
        'user': ['create', 'delete', 'hard_delete'],
    }
}
enchance_only_perms = ['foo.delete', 'foo.hard_delete']


@fixturerouter.get('/init', summary="Groups, Permissions, and relationships")
async def setup_init():
    try:
        # Create groups and permissions
        permlist = []
        for groupname, val in perms.items():
            group = await Group.create(name=groupname)
            for app, actions in val.items():
                for i in actions:
                    code = f'{app}.{i}'
                    if code  in permlist:
                        continue
                    await Permission.create(
                        name=f'{app.capitalize()} {i.capitalize()}', code=code
                    )
                    permlist.append(code)
        
        # Set permissions to groups
        for groupname, val in perms.items():
            group = await Group.get(name=groupname).only('id', 'name')
            ll = []
            for app, actions in val.items():
                for i in actions:
                    ll.append(f'{app}.{i}')
            permlist = await Permission.filter(code__in=ll).only('id')
            await group.permissions.add(*permlist)
            
            # Save group perms to cache as list
            red.set(s.CACHE_GROUPNAME.format(groupname), ll, ttl=-1)
            
        return True
    except Exception:
        return False


@fixturerouter.get('/users', summary="Create users")
async def create_users():
    try:
        # User 1
        usserdata = UserCreate(email=EmailStr('enchance@gmail.com'), password='pass123')
        create_user = get_create_user(userdb, UserDB)
        created_user = await create_user(usserdata, safe=True)
        ret = created_user
        groups = await Group.filter(name__in=s.USER_GROUPS)
        
        user = await UserMod.get(pk=created_user.id)
        user.is_verified = True
        user.is_superuser = True
        await user.save()
        await user.groups.add(*groups)
        
        # Perms for User 1
        ll = []
        userperms = await Permission.filter(code__in=enchance_only_perms).only('id')
        for perm in userperms:
            ll.append(UserPermissions(user=user, permission=perm, author=user))
        await UserPermissions.bulk_create(ll)
        
        # User 2
        usserdata = UserCreate(email=EmailStr('unverified@gmail.com'), password='pass123')
        create_user = get_create_user(userdb, UserDB)
        created_user = await create_user(usserdata, safe=True)
        groups = await Group.filter(name__in=s.USER_GROUPS)
        user = await UserMod.get(pk=created_user.id)
        await user.groups.add(*groups)
        
        return ret
    
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )


@fixturerouter.get('/options', summary='Don\'t run if you haven\'t created users yet')
async def create_options():
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

