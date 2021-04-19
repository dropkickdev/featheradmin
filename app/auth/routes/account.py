from fastapi import APIRouter, Depends, Response

from app.auth import current_user



accountrouter = APIRouter()

# TESTME: Untested
@accountrouter.patch('/group', summary='Add group to user')
def add_group(_: Response, user=Depends(current_user)):
    pass

# TESTME: Untested
@accountrouter.delete('/group', summary='Remove group from user')
def remove_group(_: Response, user=Depends(current_user)):
    pass

# TESTME: Untested
@accountrouter.patch('/permission', summary='Add permission to user')
def add_permission(_: Response, user=Depends(current_user)):
    pass

# TESTME: Untested
@accountrouter.delete('/permission', summary='Remove permission from user')
def remove_permission(_: Response, user=Depends(current_user)):
    pass