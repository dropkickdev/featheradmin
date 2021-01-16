# from fastapi import HTTPException
# from starlette import status
#
#
# XEMAIL_EXISTS = HTTPException(
#     status_code=status.HTTP_400_BAD_REQUEST,
#     detail=_("Email already exists.")
# )
#
# XUSERNAME_EXISTS = HTTPException(
#     status_code=status.HTTP_400_BAD_REQUEST,
#     detail=_("Username already exists.")
# )
#
# XUNAUTHORIZED = HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail=_("Unauthorized access"),
#     headers={"WWW-Authenticate": "Bearer"},
# )