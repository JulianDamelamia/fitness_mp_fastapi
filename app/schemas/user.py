"""Módulo que define los esquemas Pydantic para usuarios y autenticación en la aplicación de fitness."""

from typing import Optional
from pydantic import BaseModel, EmailStr


## --- USER SCHEMAS ---
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
    id: int
    email: str
    message: Optional[str] = None


class UserProfileResponse(UserBase):
    id: int
    email: EmailStr
    message: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
