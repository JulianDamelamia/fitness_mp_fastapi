from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(UserBase):
    username_or_email: str
    password: str

class UserResponse(UserBase):
    message: str

class UserProfileResponse(UserBase):
    email: EmailStr
    full_name: Optional[str] = None
    message: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str