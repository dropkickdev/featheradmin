from fastapi import APIRouter, Depends, Response, status, Body

from app import ic
from app.auth import current_user, UserDBComplete, UserMod



accountrouter = APIRouter()

# TESTME: Untested
@accountrouter.post('/group', summary='Add group to user', status_code=status.HTTP_201_CREATED)
async def add_group(_: Response, user=Depends(current_user), group: str = Body(...)):
    usermod = await UserMod.get_or_none(email=user.email).only('id')
    groups = await usermod.add_group(group)
    return groups
    

# TESTME: Untested
@accountrouter.delete('/group', summary='Remove group from user')
async def remove_group(_: Response, user=Depends(current_user)):
    pass

# TESTME: Untested
@accountrouter.post('/permission', summary='Add permission to user')
async def add_permission(_: Response, user=Depends(current_user)):
    pass

# TESTME: Untested
@accountrouter.delete('/permission', summary='Remove permission from user')
async def remove_permission(_: Response, user=Depends(current_user)):
    pass