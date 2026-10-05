from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
