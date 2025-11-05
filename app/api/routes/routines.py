from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.fitness import Routine, Session as SessionModel
from app.schemas.fitness import RoutineCreate, Routine

#templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/routines", tags=["routines"])

@router.post("/", response_model=Routine)
def create_routine(routine_data: RoutineCreate, db: Session = Depends(get_db)):
    routine = Routine(name=routine_data.name)
    if routine_data.session_ids:
        sessions = db.query(SessionModel).filter(SessionModel.id.in_(routine_data.session_ids)).all()
        routine.sessions = sessions
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine

@router.get("/", response_model=list[Routine])
def get_routines(db: Session = Depends(get_db)):
    return db.query(Routine).all()

@router.get("/{routine_id}", response_model=Routine)
def get_routine(routine_id: int, db: Session = Depends(get_db)):
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return routine