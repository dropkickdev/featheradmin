from pydantic import BaseModel, EmailStr, Field



class UniqueFieldsRegistration(BaseModel):
    email: EmailStr
    username: str   = Field(..., min_length=4)
    password: str   = Field(..., min_length=4)