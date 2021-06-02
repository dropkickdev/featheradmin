from typing import Optional, Dict, Any
from fastapi import HTTPException

from app import logger
from app.settings import settings as s



UNPROCESSABLE_422 = 422
NOTFOUND_404 = 404
PERMISSIONDENIED_403 = 403
BADERROR_503 = 503


class BaseAppError(HTTPException):
    message = 'NO MESSAGE FOUND'
    status_code = UNPROCESSABLE_422
    
    def __init__(self, detail: Optional[Any] = None, *, status_code: Optional[int] = None,
                 headers: Optional[Dict[str, Any]] = None) -> None:
        detail = detail or self.message
        status_code = status_code or self.status_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(BaseAppError):
    message = "DATA NOT FOUND"
    # Not 404 since pov is from the client (422) not the app (404)
    status_code = UNPROCESSABLE_422
    
    def __init__(self, model: str = None):
        message = s.DEBUG and model and f'{model} not found' or self.message
        super().__init__(message)


class PermissionDenied(BaseAppError):
    """User doesn't have permission to do something."""
    message = 'INSUFFICIENT PERMISSIONS'
    status_code = PERMISSIONDENIED_403


class FalsyDataError(BaseAppError):
    """Data is falsy such as '', [], None, {}, set(), False, etc.."""
    message = "FALSY DATA OR NONE"
    status_code = UNPROCESSABLE_422


class UnusableDataError(BaseAppError):
    """Wrong data type"""
    message = 'DATA RECIEVED BUT CANNOT BE USED'
    status_code = UNPROCESSABLE_422

    def __init__(self, model: str = None):
        message = s.DEBUG and model and f'{model} not found' or self.message
        super().__init__(message)


class ServiceError(BaseAppError):
    """Unable to continue work because of a database error."""
    message = 'UNABLE TO PROCESS DATA'
    status_code = BADERROR_503


class AppError(BaseAppError):
    """All other errors"""
    message = 'UNABLE TO ACCESS APPLICATION AT THIS TIME'