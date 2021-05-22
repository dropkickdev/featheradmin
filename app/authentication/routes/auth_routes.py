from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.router.common import ErrorCode
from tortoise.exceptions import DoesNotExist

from app.auth import (
    fapiuser, jwtauth, current_user,
    REFRESH_TOKEN_KEY,
    update_refresh_token, create_refresh_token, refresh_cookie
)

authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router())



@authrouter.post("/login")
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends()):
    user = await fapiuser.db.authenticate(credentials)
    
    if user is None or not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    
    try:
        token = await update_refresh_token(user)
    except DoesNotExist:
        token = await create_refresh_token(user)
    
    cookie = refresh_cookie(REFRESH_TOKEN_KEY, token)
    response.set_cookie(**cookie)
    
    # TODO: Check if user data is in cache in accordance with UserDB
    
    data = {
        **await jwtauth.get_login_response(user, response),
        'is_verified': user.is_verified
    }
    if not user.is_verified:
        data.update(dict(details='User is not verified yet so user cannot log in.'))
    return data


# TESTME: Untested
@authrouter.post("/logout", dependencies=[Depends(current_user)])
async def logout(response: Response):
    """
    Logout the user by deleting all tokens. Only unexpired tokens can logout.
    """
    # TODO: Delete user's permissions from the cache
    # TODO: Delete user's groups from the cache
    
    del response.headers['authorization']
    response.delete_cookie(REFRESH_TOKEN_KEY)
