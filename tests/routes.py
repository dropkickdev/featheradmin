from fastapi import Response, APIRouter, Depends

from app import ic
from app.auth import current_user, UserMod
from .auth_test import VERIFIED_USER_ID, VERIFIED_EMAIL_DEMO


testrouter = APIRouter()


@testrouter.post('/dev_view_user_data')
async def dev_view_user_data(response: Response, user=Depends(current_user)):
    # ic(user.permissions)
    ic(type(user), user)
    # x = await UserMod.get(id=user.id).only('id', 'username', 'first_name', 'last_name')
    # ret = await x.add_perm(['profile.create', 'profile.read'])
    # ic(ret)
    return user


@testrouter.post('/dev_user_add_perm')
async def dev_user_add_perm(response: Response, user=Depends(current_user)):
    user = await UserMod.get(id=user.id).only('id', 'email')
    # user.single = await user.add_perm('user.hard_delete')
    # user.many = await user.add_perm(['user.delete', 'user.update'])
    # user_dict = user.to_dict()
    # ic(vars(user))
    return user
    