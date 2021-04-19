from fastapi import APIRouter, Depends, Response

from app.auth import current_user



accountrouter = APIRouter()


# TESTME: Untested
@accountrouter.patch('/group', summary='Add group to user')
def add_group(_: Response, user=Depends(current_user)):
    pass