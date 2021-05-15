from typing import Optional, Any
from pydantic import BaseModel, Field, validator

from app import ic


class UpdatePermissionPyd(BaseModel):
    id: int
    code: str = Field(None, max_length=20)
    name: str = Field(None, max_length=191)

    @validator('code', 'name')
    def cleanup(cls, val: Any):
        if isinstance(val, str):
            val = val.strip()
        return val


class CreateGroupPyd(BaseModel):
    name: str = Field(..., max_length=20)
    summary: str = Field('', max_length=191)
    
    @validator('name', 'summary')
    def cleanup(cls, v, field):
        if field.name == 'name' and not v:
            raise ValueError('Value cannot be empty.')
        return v.strip()


class UpdateGroupPyd(CreateGroupPyd):
    id: int
