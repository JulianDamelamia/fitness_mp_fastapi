from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session as db_Session

from app.api.dependencies import get_db, get_current_user
from app.services.routine_service import RoutineService
from app.errors.errors import EntityNotFoundError,ValidationError 
from app.models.fitness import Routine
from app.models.user import User
from app.schemas.fitness import RoutineCreate, RoutineResponse,SessionDeleteRequest
import pdb
import traceback

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
@router.get("/", response_class=HTMLResponse)
def list_routines(request:Request, db: db_Session = Depends(get_db)):
    """Muestra todas las rutinas registradas con sus sesiones
    """
    routines = db.query(Routine).all()
    return templates.TemplateResponse(
        "routine_list.html",{"request":request,"routines":routines}
    )

@router.get("/new", response_class=HTMLResponse)
def routine_form(request:Request):
    """Muestra todas las rutinas registradas con sus sesiones
    """
    return templates.TemplateResponse(
        "routine_form.html",{"request":request}
    )
@router.post("/", response_model=RoutineResponse)
def create_routine(
    routine_data: RoutineCreate, 
    db: db_Session = Depends(get_db),
    current_user: User = Depends(lambda: User(id=1, username="testuser"))#Depends(get_current_user)
    ):
    """Crea rutinas a partir de sesiones, hechas de ejercicios.
    Puede tomar ejercicios y sesiones previamente guardadas o crear nuevos
     """
    try:
        routine = RoutineService.create_routine(
            routine_data=routine_data,
            db=db,
            current_user_id= current_user.id
            )
        return routine

    except EntityNotFoundError as e:
        print("entity not found inesperado:", e)
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        print("Validation inesperado:", e)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
            print("Error inesperado:", e)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    
@router.get("/{routine_id}", response_class=HTMLResponse)
def get_routine(request: Request, routine_id: int, db: db_Session = Depends(get_db)):
    """Muestra el detalle de una rutina específica
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    return templates.TemplateResponse(
        "routine_detail.html",{"request":request,"routine":routine}
    )



@router.delete("/{routine_id}", response_class=RedirectResponse)
def delete_routine(routine_id: int, db: db_Session = Depends(get_db)):
    """Elimina una rutina y redirige al listado.
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    db.delete(routine)
    db.commit()
    return RedirectResponse(url="/routines", status_code=status.HTTP_303_SEE_OTHER)


@router.patch("/{routine_id}", response_model=RoutineResponse)
def update_routine(
    routine_id: int,
    routine_data: RoutineCreate,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(lambda: User(id=1, username="testuser"))
):
    """Actualiza una rutina referenciada por su id
    """
    try:
        routine = RoutineService.update_routine(routine_id, routine_data, db, current_user.id)
        return routine
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")
    
@router.delete("/{routine_id}/sessions")
def delete_routine_sessions(
    routine_id: int,
    request: SessionDeleteRequest,
    db=Depends(get_db),
    current_user: User = Depends(lambda: User(id=1, username="testuser"))
):
    """Elimina una o más sesiones específicas de una rutina."""
    routine = db.query(Routine).filter_by(id=routine_id, creator_id=current_user.id).first()
    if not routine:
        raise EntityNotFoundError(f"Rutina con ID {routine_id} no encontrada")

    deleted_ids = RoutineService.delete_sessions(routine, request.session_ids, db)
    db.commit()

    return {"detail": f"Sesiones eliminadas correctamente", "deleted_ids": deleted_ids}

@router.get("/html", response_class=HTMLResponse)
def list_routines(request:Request, db: db_Session = Depends(get_db)):
    """Muestra todas las rutinas registradas con sus sesiones
    """
    routines = db.query(Routine).all()
    return templates.TemplateResponse(
        "routine_list.html",{"request":request,"routines":routines}
    )

@router.get("/html/{routine_id}", response_class=HTMLResponse)
def get_routine(request: Request, routine_id: int, db: db_Session = Depends(get_db)):
    """Muestra el detalle de una rutina específica
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    return templates.TemplateResponse(
        "routine_detail.html",
        {"request": request, "routine": routine}
    )
