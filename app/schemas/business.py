from pydantic import BaseModel
from typing import List, Optional
from app.schemas.fitness import Routine

class PlanBase(BaseModel):
    name: str
    price: int

class PlanCreate(PlanBase):
    routine_ids: Optional[List[int]] = []

class Plan(PlanBase):
    id: int
    routines: List[Routine] = []
    class Config:
        orm_mode = True