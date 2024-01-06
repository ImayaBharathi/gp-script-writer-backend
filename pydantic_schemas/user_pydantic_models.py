from pydantic import BaseModel, EmailStr

import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "your-access-token",
                "refresh_token": "your-refresh-token",
                "token_type": "bearer"
            }
        }

class UserDetailsBase(BaseModel):
    user_id: uuid.UUID
    other_info: dict

class UserDetailsCreate(UserDetailsBase):
    pass

class UserDetails(UserDetailsBase):
    user_details_id: uuid.UUID

    class Config:
        from_attributes = True
