from fastapi import Response, APIRouter, Depends

from app import ic
from app.auth import current_user, UserMod, userdb
from .auth_test import VERIFIED_USER_ID, VERIFIED_EMAIL_DEMO
from app.auth import UserDB


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
async def dev_user_add_perm(response: Response, user=Depends(current_user)):
    user = await UserMod.get(id=user.id).only('id', 'email')
    user.single = await user.add_perm('user.read')
    user.many = await user.add_perm(['user.delete', 'user.update'])
    
    user_dict = await user.to_dict()
    user = UserDB(**user_dict)
    return user
