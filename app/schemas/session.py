"""Módulo que define los esquemas Pydantic para sesiones de entrenamiento
y registros de ejercicios en la aplicación de fitness."""

from typing import List

from datetime import date
from pydantic import BaseModel, Field


# entradas para crear sesión
class ExerciseInSession(BaseModel):
    exercise_id: int
    weight: float
    reps: List[int] = Field(..., example=[10, 8, 8])

    class Config:
        from_attributes = True


class CreateSessionSchema(BaseModel):
    session_id: int
    date: date
    exercises: List[ExerciseInSession]


# salidas para devolver sesión completa
class ExerciseLogOut(BaseModel):
    id: int
    exercise_name: str
    weight: float
    reps: List[int]

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    name: str
    date: date
    exercises: List[ExerciseLogOut]

    class Config:
        from_attributes = True
