from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.fitness import Session as FitnessSession
from app.models.fitness import Exercise
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(FitnessSession)
        .filter(FitnessSession.creator_id == current_user.id)
        .all()
    )
    return templates.TemplateResponse(
        "session_list.html", {"request": request, "sessions": sessions}
    )


@router.get("/new", response_class=HTMLResponse)
def create_session_form(request: Request):
    # Mostramos el formulario
    return templates.TemplateResponse("session_form.html", {"request": request})


@router.post("/new")
def create_session(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Creamos la sesión básica
    new_session = FitnessSession(session_name=name, creator_id=current_user.id)
    db.add(new_session)
    db.commit()
    return RedirectResponse(url="/sessions", status_code=303)


@router.get("/{session_id}", response_class=HTMLResponse)
def get_session_detail(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Muestra el detalle de una sesión, incluyendo sus ejercicios.
    """
    session = (
        db.query(FitnessSession)
        .filter(
            FitnessSession.id == session_id,
            FitnessSession.creator_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404, detail="Sesión no encontrada o no te pertenece"
        )

    return templates.TemplateResponse(
        "session_detail.html", {"request": request, "session": session}
    )


@router.post("/{session_id}/add_exercise")
def add_exercise_to_session(
    session_id: int,
    exercise_name: str = Form(...),
    target_sets: int = Form(...),
    target_reps: int = Form(...),
    target_weight: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Añade un nuevo ejercicio a una sesión existente.
    """
    session = (
        db.query(FitnessSession)
        .filter(
            FitnessSession.id == session_id,
            FitnessSession.creator_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404, detail="Sesión no encontrada o no te pertenece"
        )

    new_exercise = Exercise(
        exercise_name=exercise_name,
        target_sets=target_sets,
        target_reps=target_reps,
        target_weight=target_weight,
        session_id=session_id,
    )

    db.add(new_exercise)
    db.commit()

    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)


@router.post("/exercise/{exercise_id}/delete")
def delete_exercise_from_session(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina un ejercicio específico.
    Verifica que el ejercicio pertenezca a una sesión del usuario.
    """
    exercise_to_delete = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise_to_delete:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    # Nos aseguramos de que la sesión a la que pertenece este ejercicio
    # sea propiedad del usuario logueado.
    session_owner_id = exercise_to_delete.session.creator_id
    if session_owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para borrar este ejercicio"
        )

    session_id = exercise_to_delete.session_id

    db.delete(exercise_to_delete)
    db.commit()

    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/delete")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina una sesión completa y todos sus ejercicios asociados.
    """
    # Buscamos la sesión
    session_to_delete = (
        db.query(FitnessSession)
        .filter(
            FitnessSession.id == session_id,
            FitnessSession.creator_id == current_user.id,
        )
        .first()
    )

    if not session_to_delete:
        raise HTTPException(
            status_code=404, detail="Sesión no encontrada o no te pertenece"
        )

    db.delete(session_to_delete)
    db.commit()

    return RedirectResponse(url="/sessions", status_code=303)
