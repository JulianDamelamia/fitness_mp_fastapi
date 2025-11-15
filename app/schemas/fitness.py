"""Módulo que define los esquemas Pydantic para rutinas, sesiones y ejercicios
en la aplicación de fitness."""

# app/schemas/fitness.py
from typing import List, Optional
from pydantic import BaseModel


## --- SCHEMAS ejercicio ---
class ExerciseBase(BaseModel):
    exercise_name: str
    target_sets: int
    target_reps: int
    target_weight: Optional[float] = None
    primary_muscles: Optional[List[str]] = None
    secondary_muscles: Optional[List[str]] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int

    class ConfigDict:
        from_attributes = True


## --- SCHEMAS sesiones ---
class SessionBase(BaseModel):
    session_name: Optional[str] = None
    id: Optional[int] = None


class SessionCreate(SessionBase):
    exercises: List[ExerciseCreate] = []


class SessionResponse(SessionBase):
    id: int
    exercises: List[ExerciseResponse]

    class ConfigDict:
        from_attributes = True


class SessionDeleteRequest(BaseModel):
    """Cuerpo de una solicitud para eliminar sesiones de una rutina"""

    session_ids: List[int]


## --- SCHEMAS rutinas ---
class RoutineBase(BaseModel):
    name: str


class RoutineCreate(RoutineBase):
    sessions: List[SessionCreate] = []


class RoutineResponse(RoutineBase):
    id: int
    creator_id: int
    sessions: Optional[List[SessionResponse]] = None

    class ConfigDict:
        from_attributes = True
