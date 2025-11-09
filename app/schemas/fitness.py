# app/schemas/fitness.py
from pydantic import BaseModel
from typing import List, Optional

## --- SCHEMAS ejercicio ---
# Schema base con campos comunes para ejercicios
class ExerciseBase(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None   
    session_name: Optional[str] = None

class SessionCreate(SessionBase):
    exercises: List[ExerciseCreate] = []

class SessionResponse(SessionBase):
    id: int
    exercises: List[ExerciseResponse]

    class ConfigDict:
        from_attributes = True

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

