from redis.exceptions import ResponseError
from fastapi import APIRouter, HTTPException, status, FastAPI
from fastapi_users.user import get_create_user
from fastapi_users.user import UserAlreadyExists
from fastapi_users.router.common import ErrorCode
from pydantic import EmailStr

from app import red, ic
from app.settings import settings as s
from app.auth import userdb, UserDB, UserCreate, UserMod
from app.auth.models.rbac import Group, Permission, UserPermissions
from app.auth.models.core import Option
from tests.auth_test import VERIFIED_USER_DEMO
from fixtures.permissions import ContentGroup, AccountGroup, StaffGroup, AdminGroup



app = FastAPI()
fixturerouter = APIRouter()

perms = {
    'ContentGroup': ContentGroup,
    'AccountGroup': AccountGroup,
    'StaffGroup': StaffGroup,
    'AdminGroup': AdminGroup,
    'NoaddGroup': {
        'foo': ['read', 'update', 'delete', 'hard_delete'],
        'user': ['create', 'delete', 'hard_delete'],
    }
}
enchance_only_perms = ['foo.delete', 'foo.hard_delete']
options = {
    'site': {
        'sitename': s.SITE_NAME,
        'siteurl': s.SITE_URL,
        'author': 'DropkickDev',
        'last_update': '',
    },
    'user': {
        'theme': 'Light',
        'email_notifications': True,
        'language': 'en',
    },
    'admin': {
        'access_token': s.ACCESS_TOKEN_EXPIRE,
        'refresh_token': s.REFRESH_TOKEN_EXPIRE,
        'refresh_token_cutoff': s.REFRESH_TOKEN_CUTOFF,
        'verify_email': s.VERIFY_EMAIL
    }
}


@fixturerouter.get('/init', summary="Groups, Permissions, and relationships")
async def init():
    try:
        # Create groups and permissions
        permlist = []
        for groupname, val in perms.items():
            group = await Group.create(name=groupname)
            for app, actions in val.items():
                for i in actions:
                    code = f'{app}.{i}'
                    if code in permlist:
                        continue
                    await Permission.create(
                        name=f'{app.capitalize()} {i.capitalize()}', code=code
                    )
                    permlist.append(code)
        
        for groupname, data in perms.items():
            group = await Group.get(name=groupname).only('id', 'name')
            ll = []
            for part, actions in data.items():
                for i in actions:
                    ll.append(f'{part}.{i}')
            permlist = await Permission.filter(code__in=ll).only('id')
            await group.permissions.add(*permlist)
            
            try:
                # Save group perms to cache as list
                red.set(s.CACHE_GROUPNAME.format(groupname), ll, ttl=-1)
            except ResponseError:
                pass
            
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
        users = await UserMod.all().only('id')
        if not users:
            return 'foo'
        ll = []
        for cat, data in options.items():
            for name, val in data.items():
                if cat == 'user':
                    for user in users:
                        ll.append(Option(name=name, value=val, user_id=user.id))
                elif cat == 'site':
                    ll.append(Option(name=name, value=val))
                elif cat == 'admin':
                    ll.append(Option(name=name, value=val, admin_only=True))
        await Option.bulk_create(ll)
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

