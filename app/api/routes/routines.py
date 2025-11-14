from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as db_Session
from typing import List, Optional

from app.api.dependencies import get_db, get_current_user
from app.models.fitness import Routine, Session as FitnessSession
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Ver rutinas
@router.get("/", response_class=HTMLResponse)
def list_routines(
    request: Request,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    routines = db.query(Routine).filter(Routine.creator_id == current_user.id).all()
    
    return templates.TemplateResponse(
        "routine_list.html", 
        {"request": request, "routines": routines}
    )

# Formulario para crear nueva rutina
@router.get("/new", response_class=HTMLResponse)
def create_routine_form(
    request: Request,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Necesitamos pasarle las sesiones existentes para que el usuario elija
    sessions = db.query(FitnessSession).filter(FitnessSession.creator_id == current_user.id).all()
    
    return templates.TemplateResponse(
        "routine_form.html",
        {
            "request": request, 
            "sessions": sessions,
            "form_data": {},
            "errors": {},
            "action_url": "/routines/new" # Definimos a dónde manda los datos
        }
    )

# Procesar el formulario de creación
@router.post("/new")
def create_routine(
    name: str = Form(...),
    session_ids: List[int] = Form([]),
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validar nombre
    if not name.strip():
        sessions = db.query(FitnessSession).all()
        return templates.TemplateResponse(
            "routine_form.html",
            {
                "request": {}, "sessions": sessions,
                "errors": {"name": "El nombre es obligatorio"},
                "form_data": {"name": name}
            }
        )

    # Crear la Rutina
    new_routine = Routine(name=name, creator_id=current_user.id)
    
    # Asociar las sesiones seleccionadas
    if session_ids:
        selected_sessions = db.query(FitnessSession).filter(FitnessSession.id.in_(session_ids)).all()
        new_routine.sessions.extend(selected_sessions)

    db.add(new_routine)
    db.commit()

    return RedirectResponse(url="/routines", status_code=303)


# Detalle de una rutina
@router.get("/{routine_id}", response_class=HTMLResponse)
def get_routine_detail(
    request: Request, 
    routine_id: int, 
    db: db_Session = Depends(get_db)
):
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    return templates.TemplateResponse(
        "routine_detail.html",
        {"request": request, "routine": routine}
    )


# Eliminar una rutina
@router.post("/{routine_id}/delete")
def delete_routine(routine_id: int, db: db_Session = Depends(get_db)):
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    db.delete(routine)
    db.commit()
    return RedirectResponse(url="/routines", status_code=303)