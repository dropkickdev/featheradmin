from fastapi import Response, APIRouter, Depends, Body, Header, HTTPException
from fastapi.concurrency import contextmanager_in_threadpool
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from limeutils import listify
from pydantic import ValidationError




# from app import ic, red, exceptions as x
# from app.settings import settings as s
# from app.authentication import (
#     TokenMod, Authcontrol, Authutils, jwtauth,
#     current_user, UserMod, userdb, Permission, Group,
#     UserDB, UserDBComplete, tokenonly
# )
# from .auth_test import VERIFIED_ID_DEMO, VERIFIED_EMAIL_DEMO
#
#
# testrouter = APIRouter()
#
#
# @testrouter.post('/dev_user_data')
# async def dev_user_data(_: Response, user=Depends(current_user)):
#     return user
#
#
# @testrouter.get('/open')
# async def open(_: Response):
#     if s.DEBUG:
#         raise x.NotFoundError('UserMod')







# async def rollback_groups(user, rollback):
#     """
#     Rollback any groups which added to a user
#     :param user:        From current_user
#     :param rollback:    List of group names to rollback
#     :return:            bool
#     """
#     # DB
#     to_drop = await Group.filter(name__in=rollback).only('id')
#     usermod = await UserMod.get(pk=user.id).only('id')
#     await usermod.groups.remove(*to_drop)
#
#     # Redis
#     grouplist = await Group.filter(name__in=s.USER_GROUPS).values('name')
#     names = [i.get('name') for i in grouplist]
#     red.set(f'user-{str(user.id)}', dict(groups=makesafe(names)))
#
#     return True
#
#
# @testrouter.post('/dev_user_add_group')
# async def dev_user_add_group(response: Response, user=Depends(current_user),
#                         access_token=Depends(tokenonly), groups=Body(...)):
#     # Rollback
#     if groups == 'rollback':
#         return await rollback_groups(user, ['StaffGroup', 'AdminGroup', 'ContributorGroup'])
#
#     usermod = await UserMod.get(id=user.id).only('id', 'email')
#     groups = listify(groups)
#     await usermod.add_group(*groups)
#
#     user = await jwtauth(access_token, userdb)
#     return user
#
#
# @testrouter.post('/dev_user_has_group')
# async def dev_user_has_group(response: Response, user=Depends(current_user), groups=Body(...)):
#     groups = groups.get('groups')
#     groups = listify(groups)
#     usermod = await UserMod.get(pk=user.id)
#     return await usermod.has_group(*groups)
#
#
# @testrouter.post('/dev_user_has_perms')
# async def dev_user_has_perms(response: Response, user=Depends(current_user), perms=Body(...)):
#     # TODO: See if you can get the user from the cache
#     usermod = await UserMod.get(id=user.id).only('id')
#     perms = listify(perms)
#     return await usermod.has_perms(*perms)
#
#
# @testrouter.post('/dev_token')
# async def new_access_token(response: Response):
#     """
#     Modified '/authentication/token' route from app.authentication.routes. Highly modified. Not a good reference.
#     """
#
#     # FOR TESTING ONLY
#     REFRESH_TOKEN_KEY = 'refresh_token'
#     token = await TokenMod.get(author_id=VERIFIED_USER_DEMO, is_blacklisted=False)
#     refresh_token = token.token
#
#     try:
#         # if refresh_token is None:
#         #     raise Exception
#
#         # token = await TokenMod.get(token=refresh_token, is_blacklisted=False) \
#         #     .only('id', 'token', 'expires', 'author_id')
#         user = await userdb.get(token.author_id)    # noqa
#
#         mins = Authutils.expires(token.expires)
#         ic(mins)
#         test_message = 'STILL OK'
#         if mins <= 0:
#             raise Exception
#         elif mins <= 30:
#             test_message = 'REFRESH ANYWAY'
#             # refresh the refresh_token anyway before it expires
#             try:
#                 token = await Authcontrol.update_refresh_token(user, token=token)
#             except DoesNotExist:
#                 token = await Authcontrol.create_refresh_token(user)
#
#             cookie = Authcontrol.refresh_cookie(REFRESH_TOKEN_KEY, token)
#             # response.set_cookie(**cookie)
#
#         ic(test_message)
#         return await jwtauth.get_login_response(user, response)
#
#     except (DoesNotExist, Exception) as e:
#         test_message = 'EXPIRED'
#         ic(test_message)
#         # del response.headers['authorization']
#         # response.delete_cookie(REFRESH_TOKEN_KEY)
#         return dict(access_token='')
#
#
# @testrouter.post('/dev_remove_user_permissions')
# async def dev_remove_permissions(response: Response, user=Depends(current_user)):
#     usermod = await UserMod.get(pk=user.id)
#     # Get current perms
#     # Add some new ones
#     # Delete and compare
#     user = await UserMod.get(pk=user.id).only('id')
#     ic(await user.get_permissions())
#     # return await usermod.remove_permission()












# TODO: Rollback
# @testrouter.post('/dev_user_add_perm')
# async def dev_add_perm(response: Response, user=Depends(current_user)):
#     user = await UserMod.get(id=user.id).only('id', 'email')
#     await user.add_permission('user.read')
#     await user.add_permission(['user.delete', 'user.update'])
#
#     # Manually get the value of current_user since it's been updated
#     user_dict = await user.to_dict()
#     user = UserDBComplete(**user_dict)
#     return user
