from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.fitness import Session as FitnessSession, Exercise, Routine
from app.models.user import User
from app.models.tracker import SessionLog, ExerciseLog
from app.models.business import Purchase, Plan
from app.models.associations import routines_sessions, plans_routines

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/session/{session_id}", response_class=HTMLResponse)
def start_session_tracking(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Muestra la página de tracking para una sesión de plantilla.
    """
    # Buscamos la sesión de plantilla (ej. "Día de Pecho")
    session = db.query(FitnessSession).options(
        joinedload(FitnessSession.exercises)
    ).filter(
        FitnessSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o no te pertenece")

    # Comprobamos si el usuario es el creador
    is_creator = (session.creator_id == current_user.id)

    # Comprobamos si el usuario tiene acceso por compra
    # (Buscamos si existe una compra, de este usuario, a un plan,
    # que contenga una rutina, que contenga esta sesión)
    has_purchased_access = db.query(Purchase.id)\
        .join(Plan, Plan.id == Purchase.plan_id)\
        .join(plans_routines, plans_routines.c.plan_id == Plan.id)\
        .join(Routine, Routine.id == plans_routines.c.routine_id)\
        .join(routines_sessions, routines_sessions.c.routine_id == Routine.id)\
        .filter(Purchase.user_id == current_user.id)\
        .filter(routines_sessions.c.session_id == session_id)\
        .first() # .first() es más rápido, solo nos importa si existe (1) o no (None)

    # Si no es creador Y tampoco tiene acceso por compra, lo rechazamos.
    if not is_creator and not has_purchased_access:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o no te pertenece")

    return templates.TemplateResponse("track_session.html", {
        "request": request,
        "session": session 
    })

@router.post("/log_session")
async def log_session(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recibe el formulario de track_session.html y guarda el entrenamiento
    en los modelos SessionLog y ExerciseLog.
    """
    
    # Parsear el formulario
    form_data = await request.form()
    
    # Obtener el ID de la sesión plantilla
    session_template_id = form_data.get("session_template_id")
    if not session_template_id:
        raise HTTPException(status_code=400, detail="Falta session_template_id")

    # Verificamos que la sesión plantilla exista y sea del usuario
    session_template = db.query(FitnessSession).filter(
        FitnessSession.id == session_template_id
    ).first()

    if not session_template:
        raise HTTPException(status_code=404, detail="Sesión plantilla no encontrada")

    # Crear el SessionLog (el "entrenamiento" general)
    new_session_log = SessionLog(
        date=datetime.now(),
        session_id=session_template.id,
        user_id=current_user.id
    )
    db.add(new_session_log)
    db.commit()
    db.refresh(new_session_log)

    # Iterar sobre los ejercicios de la plantilla y guardar sus logs
    for exercise_template in session_template.exercises:
        
        # Construimos los nombres de los campos del formulario
        weight_key = f"exercise.{exercise_template.id}.weight"
        reps_key = f"exercise.{exercise_template.id}.reps"

        weight = form_data.get(weight_key)
        reps_list = form_data.getlist(reps_key)

        if not weight or not reps_list:
            # Omitir si faltan datos para este ejercicio
            continue 

        # Crear un ExerciseLog por CADA SERIE (set)
        for set_index, reps_count in enumerate(reps_list):
            set_number = set_index + 1
            
            if not reps_count:
                continue

            exercise_log_entry = ExerciseLog(
                weight=float(weight),
                reps=int(reps_count),
                set_n=set_number,
                session_log_id=new_session_log.id,
                exercise_id=exercise_template.id
            )
            db.add(exercise_log_entry)

    # Guardar todos los ExerciseLogs
    db.commit()

    # Redirigimos al nuevo historial
    return RedirectResponse(url="/track/history", status_code=303)


@router.get("/history", response_class=HTMLResponse)
def get_tracking_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Muestra una lista de todos los entrenamientos (SessionLogs)
    que el usuario ha registrado.
    """
    
    # Buscamos todos los logs de sesiones que pertenecen
    # a plantillas creadas por el usuario actual
    logs = db.query(SessionLog)\
        .filter(SessionLog.user_id == current_user.id)\
        .order_by(SessionLog.date.desc())\
        .options(
            joinedload(SessionLog.session), # Carga el nombre de la sesión
            joinedload(SessionLog.exercise_logs).joinedload(ExerciseLog.exercise) # Carga los sets Y el nombre del ejercicio
        ).all()
        
    return templates.TemplateResponse("history.html", {
        "request": request,
        "logs": logs
    })