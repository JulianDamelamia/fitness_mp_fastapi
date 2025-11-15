"""Rutas de la API para la gestión de rutinas de fitness."""

import traceback

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session as db_Session
from sqlalchemy.orm import joinedload

# Imports de ambas ramas
from app.api.dependencies import get_db, get_current_user
from app.models.fitness import Routine
from app.models.fitness import Session as FitnessSession
from app.models.user import User
from app.services.routine_service import RoutineService
from app.errors.errors import EntityNotFoundError, ValidationError
from app.schemas.fitness import RoutineCreate, RoutineResponse, SessionDeleteRequest


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ---
# Rutas HTML (para ver la lista, el detalle y la página del form)
# ---


@router.get("/", response_class=HTMLResponse)
def list_routines(
    request: Request,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (HTML) Muestra las rutinas creadas por el usuario logueado.
    """
    routines = db.query(Routine).filter(Routine.creator_id == current_user.id).all()
    return templates.TemplateResponse(
        "routine_list.html", {"request": request, "routines": routines}
    )


@router.get("/new", response_class=HTMLResponse)
def new_routine_page(
    request: Request,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Buscamos las sesiones existentes del usuario
    sessions_models = (
        db.query(FitnessSession)
        .filter(FitnessSession.creator_id == current_user.id)
        .options(joinedload(FitnessSession.exercises))
        .all()
    )

    sessions_serializable = []
    for s in sessions_models:
        sessions_serializable.append(
            {
                "id": s.id,
                "session_name": s.session_name,
                "exercises": [
                    {
                        "exercise_name": ex.exercise_name,
                        "target_sets": ex.target_sets,
                        "target_reps": ex.target_reps,
                        "target_weight": ex.target_weight,
                    }
                    for ex in s.exercises
                ],
            }
        )

    return templates.TemplateResponse(
        "routine_form.html", {"request": request, "sessions": sessions_serializable}
    )


@router.get("/{routine_id}", response_class=HTMLResponse)
def get_routine_detail(
    request: Request,
    routine_id: int,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (HTML) Muestra el detalle de una rutina específica.
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Chequeo de seguridad
    if routine.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para ver esta rutina"
        )

    return templates.TemplateResponse(
        "routine_detail.html", {"request": request, "routine": routine}
    )


@router.post("/{routine_id}/delete")
def delete_routine_from_form(
    routine_id: int,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (HTML) Elimina una rutina desde el formulario de 'routine_list.html'.
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Chequeo de seguridad
    if routine.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para borrar esta rutina"
        )

    db.delete(routine)
    db.commit()
    return RedirectResponse(url="/routines", status_code=status.HTTP_303_SEE_OTHER)


# ---
# Rutas API Json (Usadas por el script de 'routine_form.html')
# ---


@router.post("/", response_model=RoutineResponse)
def create_routine_api(
    routine_data: RoutineCreate,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (API JSON) Recibe el JSON del script de 'routine_form.html'.
    """
    try:
        routine = RoutineService.create_routine(
            routine_data=routine_data, db=db, current_user_id=current_user.id
        )
        return routine
    except EntityNotFoundError as e:
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@router.patch("/{routine_id}", response_model=RoutineResponse)
def update_routine_api(
    routine_id: int,
    routine_data: RoutineCreate,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (API JSON) Actualiza una rutina referenciada por su id.
    """
    try:
        routine = RoutineService.update_routine(
            routine_id, routine_data, db, current_user.id
        )
        return routine
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


@router.delete("/{routine_id}/sessions")
def delete_routine_sessions_api(
    routine_id: int,
    request: SessionDeleteRequest,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    (API JSON) Elimina una o más sesiones específicas de una rutina.
    """
    routine = (
        db.query(Routine).filter_by(id=routine_id, creator_id=current_user.id).first()
    )
    if not routine:
        raise EntityNotFoundError(f"Rutina con ID {routine_id} no encontrada")

    deleted_ids = RoutineService.delete_sessions(routine, request.session_ids, db)
    db.commit()

    return {"detail": "Sesiones eliminadas correctamente", "deleted_ids": deleted_ids}
