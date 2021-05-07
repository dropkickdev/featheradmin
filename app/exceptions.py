from typing import Optional, Dict, Any
from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist



# class NoUserFound(DoesNotExist):
#     message = 'No user found with that id/email'
#
#     def __init__(self, *args, **kwargs):
#         args = args or (self.message,)
#         super().__init__(*args, **kwargs)


class PermissionDenied(HTTPException):
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "You don't have the permissions to do that"
        status_code = status_code or 403
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserNotFound(HTTPException):
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "User not found"
        status_code = status_code or 404
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class GroupNotFound(HTTPException):
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "Group not found"
        status_code = status_code or 404
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class FalseyDataError(HTTPException):
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "Submitted data is falsy such as an empty string or None"
        status_code = status_code or 422
        super().__init__(status_code=status_code, detail=detail, headers=headers)
