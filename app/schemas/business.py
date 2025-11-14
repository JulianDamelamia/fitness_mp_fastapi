from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: int


class PlanCreate(PlanBase):
    pass


class Plan(PlanBase):
    id: int
    trainer_id: int

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    plan_id: int


class Purchase(BaseModel):
    id: int
    user_id: int
    plan_id: int
    created_at: datetime
    plan: Plan  # Detalles del plan comprado

    class Config:
        from_attributes = True
