from typing import Optional
from pydantic import BaseModel, Field


# TODO: Relocate. This should be in auth
class UpdatePermissionPy(BaseModel):
    id: int
    code: str = Field(None, max_length=20)
    name: str = Field(None, max_length=191)