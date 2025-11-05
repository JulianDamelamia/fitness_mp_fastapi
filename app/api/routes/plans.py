from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.business import Plan
from app.models.fitness import Routine
from app.schemas.business import PlanCreate, Plan

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("/", response_model=Plan)
def create_plan(plan_data: PlanCreate, db: Session = Depends(get_db)):
    plan = Plan(name=plan_data.name, price=plan_data.price)
    if plan_data.routine_ids:
        routines = db.query(Routine).filter(Routine.id.in_(plan_data.routine_ids)).all()
        plan.routines = routines
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/", response_model=list[Plan])
def get_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()

@router.get("/{plan_id}", response_model=Plan)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter_by(id=plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
