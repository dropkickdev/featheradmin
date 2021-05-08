from typing import Optional, Dict, Any
from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from app.settings import settings as s



BASE_STATUS_CODE = 422
NOTFOUND_STATUS_CODE = 404
PERMISSIONDENIED_STATUS_CODE = 403
BADERROR_STATUS_CODE = 503


class BaseAppError(HTTPException):
    message = 'No message found'
    status_code = BASE_STATUS_CODE
    
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or self.message
        status_code = status_code or self.status_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(BaseAppError):
    message = "Data not found"
    def __init__(self, model: str = ''):
        message = s.DEBUG and model and f'{model} not found' or self.message
        super().__init__(detail=message)


class PermissionDenied(BaseAppError):
    """User doesn't have permission to do something."""
    message = "You don't have the permissions to do that"
    status_code = PERMISSIONDENIED_STATUS_CODE


class FalsyDataError(BaseAppError):
    """Data is falsy such as '', [], None, {}, set(), False, etc.."""
    message = "Submitted data is falsy or None"


class BadError(BaseAppError):
    """Unable to continue work because of a database error."""
    message = "Unable to process your data at this time"
    status_code = BADERROR_STATUS_CODE