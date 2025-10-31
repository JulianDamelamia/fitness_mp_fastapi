"""
BORRAR, FUE MODULARIZADO EN CARPETA SCHEMAS
from pydantic import BaseModel, EmailStr
from typing import Optional, List

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
    message: str

class UserProfileResponse(UserBase):
    id: int
    email: EmailStr
    message: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

## --- EXERCISE SCHEMAS ---
# Schema base con campos comunes para ejercicios
class ExerciseBase(BaseModel):
    name: str
    primary_muscles: List[str]
    secondary_muscles: List[str]

# Schema para crear un nuevo ejercicio
class ExerciseCreate(ExerciseBase):
    pass

# Schema para leer un ejercicio desde la API
class Exercise(ExerciseBase):
    id: int

    class Config:
        from_attributes = True # Allows Pydantic to read from ORM models"""