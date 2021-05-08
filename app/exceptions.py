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
    """User doesn't have permission to do something."""
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "You don't have the permissions to do that"
        super().__init__(status_code=403, detail=detail, headers=headers)


class UserNotFound(HTTPException):
    """A UserMod doesn't exist in the database."""
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "User not found"
        super().__init__(status_code=404, detail=detail, headers=headers)


class GroupNotFound(HTTPException):
    """A Group doesn't exist in the database."""
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "Group not found"
        super().__init__(status_code=404, detail=detail, headers=headers)


class FalsyDataError(HTTPException):
    """Data is falsy such as '', [], None, {}, set(), False, etc.."""
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or "Submitted data is falsy or None"
        super().__init__(status_code=422, detail=detail, headers=headers)
