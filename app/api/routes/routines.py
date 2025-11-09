from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session as db_Session

from app.api.dependencies import get_db, get_current_user
from app.factories.routine_factory import RoutineFactory
from app.models.fitness import Routine, Session,Exercise
from app.models.user import User
from app.schemas.fitness import RoutineCreate, RoutineResponse
import pdb

router = APIRouter(prefix="/routines", tags=["routines"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_model=list[RoutineResponse])
def list_routines(request:Request, db: db_Session = Depends(get_db)):
    """Muestra todas las rutinas registradas con sus sesiones
    """
    routines = db.query(Routine).all()
    # pdb.set_trace()
    return routines

@router.post("/", response_model=RoutineResponse)
def create_routine(
    routine_data: RoutineCreate, 
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """Crea rutinas a partir de sesiones, hechas de ejercicios.
    Puede tomar ejercicios y sesiones previamente guardadas o crear nuevos
    
    Formato JSON entrada
    {
        "name": "Str",
        "sessions": [
            {
                "id": 1 ---> sesión existente
            },
            {
                "session_name": "Día 2 - Tren inferior", ---> nueva sesión
                "exercises": [
                                { "id": 4 },
                                { "exercise_name": "Peso muerto", 
                                        "target_sets": 4, "target_reps": 6 }
                ]
            }
        ]
    }
     """
    
    routine = RoutineFactory.create_routine(routine_data, creator_id=999)
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine
    
    # for session_data in routine_data.sessions:  #procesar sesiones
    #     if getattr(session_data, "id", None):  #caso 1: sesión existente
    #         session = db.query(Session).filter(Session.id == session_data.id).first()
    #         if not session:
    #             raise HTTPException(
    #                 status_code=404,
    #                 detail=f"Session ID {session_data.id} no encontrada"
    #             )

        
    #     else:  #caso 2: crear sesión nueva
    #         if not session_data.session_name:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="Las sesiones nuevas requieren un nombre"
    #             )
    #         session = Session(session_name=session_data.session_name)
    #         db.add(session)

        
    #     if getattr(session_data, "exercises", None):  #Procesar ejercicios si existen
    #         for ex_data in session_data.exercises:
                
    #             if getattr(ex_data, "id", None):  #Caso 1: ejercicio existente
    #                 exercise = db.query(Exercise).filter(Exercise.id == ex_data.id).first()
    #                 if not exercise:
    #                     raise HTTPException(
    #                         status_code=404,
    #                         detail=f"Exercise ID {ex_data.id} no encontrado"
    #                     )
                
    #             else:  #Caso 2: nuevo ejercicio
    #                 if not ex_data.exercise_name:
    #                     raise HTTPException(
    #                         status_code=400,
    #                         detail="Los ejercicios nuevos requieren nombre"
    #                     )
    #                 exercise = Exercise(
    #                     exercise_name=ex_data.exercise_name,
    #                     target_sets=ex_data.target_sets or 0,
    #                     target_reps=ex_data.target_reps or 0,
    #                     session=session
    #                 )
    #                 db.add(exercise)
    
    #             if exercise not in session.exercises:  #Asegurar relación
    #                 session.exercises.append(exercise)

    #     sessions.append(session)

    # # vincular sesiones a la rutina
    # routine.sessions.extend(s for s in sessions if s not in routine.sessions)

    # db.add(routine)
    # db.commit()
    # db.refresh(routine)
    # return routine

@router.get("/{routine_id}", response_model=RoutineResponse)
def get_routine(request: Request, routine_id: int, db: db_Session = Depends(get_db)):
    """Muestra el detalle de una rutina específica
    """
    routine = db.query(Routine).filter_by(id=routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    return routine



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


## PELIGRO, ESTE ENDPOINT ES GIGANTE. TO-DO:modularizar (Juli)
@router.patch("/{routine_id}", response_model=RoutineResponse)
def update_routine(
    routine_id: int,
    routine_data: RoutineCreate,
    db: db_Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una rutina completa (nombre, sesiones y ejercicios).

    JSON esperado (puede incluir cualquier nivel):
    {
        "name": "Rutina actualizada",
        "sessions": [
            {
                "id": 1,                        # Sesión existente
                "session_name": "Día 1 - Push",
                "exercises": [
                    {"id": 10, "target_sets": 5},   # Edita ejercicio existente
                    {"exercise_name": "Press inclinado", "target_sets": 4, "target_reps": 8}  # Nuevo ejercicio
                ]
            },
            {
                "session_name": "Día 2 - Pierna"    # Nueva sesión completa
            }
        ]
    }
    """
    routine = db.query(Routine).filter(Routine.id == routine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Control de permisos
    if routine.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para modificar esta rutina")

    # --- Actualizar nombre ---
    if getattr(routine_data, "name", None):
        routine.name = routine_data.name

    # --- Si no hay sesiones, no tocar las existentes ---
    if not getattr(routine_data, "sessions", None):
        db.commit()
        db.refresh(routine)
        return routine

    updated_sessions = []
    for session_data in routine_data.sessions:
        # --- Sesión existente ---
        if getattr(session_data, "id", None):
            session = db.query(Session).filter(Session.id == session_data.id).first()
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session ID {session_data.id} no encontrada"
                )

            # Actualizar nombre si viene
            if getattr(session_data, "session_name", None):
                session.session_name = session_data.session_name

        # --- Nueva sesión ---
        else:
            if not session_data.session_name:
                raise HTTPException(
                    status_code=400,
                    detail="Las sesiones nuevas requieren un nombre"
                )
            session = Session(session_name=session_data.session_name)
            db.add(session)
            db.flush()

        # --- Procesar ejercicios ---
        updated_exercises = []
        if getattr(session_data, "exercises", None):
            for ex_data in session_data.exercises:
                if getattr(ex_data, "id", None): #caso 1 ejercicio existente
                    exercise = db.query(Exercise).filter(Exercise.id == ex_data.id).first()
                    if not exercise:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Exercise ID {ex_data.id} no encontrado"
                        )
                    if getattr(ex_data, "exercise_name", None):
                        exercise.exercise_name = ex_data.exercise_name
                    if getattr(ex_data, "target_sets", None) is not None:
                        exercise.target_sets = ex_data.target_sets
                    if getattr(ex_data, "target_reps", None) is not None:
                        exercise.target_reps = ex_data.target_reps

                else:  #caso 2 ejercicio nuevo
                    if not ex_data.exercise_name:
                        raise HTTPException(
                            status_code=400,
                            detail="Los ejercicios nuevos requieren nombre"
                        )
                    exercise = Exercise(
                        exercise_name=ex_data.exercise_name,
                        target_sets=ex_data.target_sets or 0,
                        target_reps=ex_data.target_reps or 0,
                        session=session
                    )
                    db.add(exercise)
                updated_exercises.append(exercise)

        if getattr(session_data, "exercises", None) is not None:
            session.exercises = updated_exercises

        updated_sessions.append(session)

    routine.sessions = updated_sessions # Reasignar sesiones completas

    db.commit()
    db.refresh(routine)
    return routine


@router.get("/html", response_class=HTMLResponse)
def list_routines(request:Request, db: db_Session = Depends(get_db)):
    """Muestra todas las rutinas registradas con sus sesiones
    """
    # pdb.set_trace()
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

## En proceso (juli)
# @router.put("/{routine_id}")
# def update_routine(
#     routine_id: int,
#     routine_data: RoutineCreate,
#     db: db_Session = Depends(get_db)
#     ):
#     """Actualiza una rutina existente con nuevas sesiones y ejercicios.
#     """
#     routine = db.query(Routine).filter_by(id=routine_id).first()
#     if not routine:
#         raise HTTPException(status_code=404, detail="Rutina no encontrada")

#     routine.name = routine_data.name

#     # Procesar sesiones
#     routine.sessions.clear()
#     for session_data in routine_data.sessions:
#         if session_data.id:
#             session = db.query(Session).filter(Session.id ==
#                                                 session_data.id).first()
#             if not session:
#                 raise HTTPException(status_code=404, 
#                         detail=f"Session ID {session_data.id} no encontrada")
#         else:
#             if not session_data.session_name:
#                 raise HTTPException(status_code=400, 
#                                     detail="Las sesiones nuevas requieren un nombre")
        
#         session = Session(session_name=session_data.session_name)
#         db.add(session)

#         if session_data.exercises:
#             for ex_data in session_data.exercises:
#                 if ex_data.id:
#                     exercise = db.query(Exercise).filter(Exercise.id ==
#                                                          ex_data.id).first()
#                     if not exercise:
#                         raise HTTPException(status_code=404, 
#                                             detail=f"Exercise ID {ex_data.id} no encontrado")
                
#                 else:
#                     if not ex_data.exercise_name:
#                         raise HTTPException(status_code=400, 
#                                             detail="Los ejercicios nuevos requieren nombre")
#                     exercise = Exercise(exercise_name=ex_data.exercise_name,
#                                         target_sets=ex_data.target_sets or 0,
#                                         target_reps=ex_data.target_reps or 0,
#                                         session=session)
#                     db.add(exercise)
                
#                 if exercise not in session.exercises:
#                     session.exercises.append(exercise)
#         if session not in routine.sessions:
#             routine.sessions.append(session)

#     db.commit()
#     db.refresh(routine)
#     return routine

# @router.post("/new", response_class=RedirectResponse)
# def new_routine_post(
#     request: Request,
#     name: str = Form(...),
#     session_ids: list[int] = Form([]),
#     db: db_Session = Depends(get_db)
# ):
#     """Crea una nueva rutina con sesiones existentes
#     """
#     errors = {}
#     if not name.strip():
#         errors["name"] = "El nombre no puede estar vacío."

#     existing = db.query(Routine).filter(Routine.name == name).first()
#     if existing:
#         errors["name"] = "Ya existe una rutina con ese nombre."

#     if errors:
#         sessions = db.query(Session).all()
#         return templates.TemplateResponse(
#             "routine_form.html",
#             {
#                 "request": request,
#                 "sessions": sessions,
#                 "form_data": {"name": name, "session_ids": session_ids},
#                 "errors": errors,
#                 "action_url": "/routines/new"
#             }
#         )

#     routine = Routine(name=name)
#     if session_ids:
#         selected_sessions = db.query(Session).filter(Session.id.in_(session_ids)).all()
#         routine.sessions = selected_sessions

#     db.add(routine)
#     db.commit()
#     db.refresh(routine)

#     return RedirectResponse(url="/routines", status_code=status.HTTP_303_SEE_OTHER)

# @router.get("/new", response_class=HTMLResponse)
# def new_routine_get(request: Request, db: db_Session = Depends(get_db)):
#     """Formulario para crear una nueva rutina
#     """

#     sessions = db.query(Session).all()
#     return templates.TemplateResponse(
#         "routine_form.html",
#         {
#             "request": request,
#             "sessions": sessions,
#             "form_data": {},
#             "errors": {},
#             "action_url": "/routines/new"
#         }
#     )
