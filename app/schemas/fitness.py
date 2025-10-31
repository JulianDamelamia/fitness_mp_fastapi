# app/schemas/fitness.py
from pydantic import BaseModel
from typing import List

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
