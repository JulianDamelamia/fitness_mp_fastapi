# app/schemas/fitness.py
from pydantic import BaseModel
from typing import List, Optional

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
        from_attributes = True # Allows Pydantic to read from ORM models


class SessionBase(BaseModel):
    name: str

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    class Config:
        orm_mode = True

class RoutineBase(BaseModel):
    name: str

class RoutineCreate(RoutineBase):
    session_ids: Optional[List[int]] = []

class Routine(RoutineBase):
    id: int
    sessions: List[Session] = []
    class Config:
        orm_mode = True