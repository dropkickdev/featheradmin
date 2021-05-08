from typing import Optional, Dict, Any
from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from app.settings import settings as s



UNPROCESSABLE_422 = 422
NOTFOUND_404 = 404
PERMISSIONDENIED_403 = 403
BADERROR_503 = 503


class BaseAppError(HTTPException):
    message = 'No message found'
    status_code = UNPROCESSABLE_422
    
    def __init__(self, *, status_code: int = None, detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or self.message
        status_code = status_code or self.status_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(BaseAppError):
    message = "Data not found"
    status_code = UNPROCESSABLE_422
    
    def __init__(self, model: str = None):
        message = s.DEBUG and model and f'{model} not found' or self.message
        super().__init__(detail=message)


class PermissionDenied(BaseAppError):
    """User doesn't have permission to do something."""
    message = "You don't have the permissions to do that"
    status_code = PERMISSIONDENIED_403


class FalsyDataError(BaseAppError):
    """Data is falsy such as '', [], None, {}, set(), False, etc.."""
    message = "Submitted data is falsy or None"
    status_code = UNPROCESSABLE_422


class BadError(BaseAppError):
    """Unable to continue work because of a database error."""
    message = "Unable to process your data at this time"
    status_code = BADERROR_503