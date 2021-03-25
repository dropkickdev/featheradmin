from fastapi import Response, APIRouter, Depends

from app import ic
from app.auth import current_user, UserMod, userdb
from .auth_test import VERIFIED_USER_ID, VERIFIED_EMAIL_DEMO
from app.auth import UserDB, UserDBComplete


testrouter = APIRouter()


@testrouter.post('/dev_view_user_data')
async def dev_view_user_data(response: Response, user=Depends(current_user)):
    # ic(user.permissions)
    # ic(type(user), user)
    # x = await UserMod.get(id=user.id).only('id', 'username', 'first_name', 'last_name')
    # ret = await x.add_perm(['profile.create', 'profile.read'])
    # ic(ret)
    return user


@testrouter.post('/dev_user_add_perm')
async def dev_add_perm(response: Response, user=Depends(current_user)):
    user = await UserMod.get(id=user.id).only('id', 'email')
    await user.add_perm('user.read')
    await user.add_perm(['user.delete', 'user.update'])
    
    user_dict = await user.to_dict()
    user = UserDBComplete(**user_dict)
    return user


@testrouter.post('/dev_user_add_group')
async def dev_add_group(response: Response, user=Depends(current_user)):
    user = await UserMod.get(id=user.id).only('id', 'email')
    await user.add_group('StaffGroup')
    await user.add_group(['AdminGroup', 'StrictdataGroup'])
    
    user_dict = await user.to_dict()
    user = UserDBComplete(**user_dict)
    return user

