# from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import RedirectResponse, HTMLResponse
# from sqlalchemy.orm import Session as db_Session
# from app.api.dependencies import get_db
# from app.models.fitness import Session
# from app.schemas.fitness import SessionCreate, SessionResponse


# router = APIRouter(prefix="/sessions", tags=["Sessions"])
# templates = Jinja2Templates(directory="app/templates")


# #listar sesiones
# @router.get("/", response_class=HTMLResponse)
# def list_sessions(request: Request, db: db_Session = Depends(get_db)):
#     """Muestra todas las sesiones."""
#     sessions = db.query(Session).all()
#     return templates.TemplateResponse(
#         "session_list.html",
#         {"request": request, "sessions": sessions}
#     )


# #formulario para crear nueva sesión
# @router.get("/new", response_class=HTMLResponse)
# def new_session_get(request: Request):
#     """Renderiza el formulario para crear una nueva sesión."""
#     return templates.TemplateResponse(
#         "session_form.html",
#         {
#             "request": request,
#             "form_data": {},
#             "errors": {},
#             "action_url": "/sessions/new", 
#         }
#     )


# # crear nueva sesión (formulario)
# @router.post("/new", response_class=HTMLResponse)
# def new_session_post(
#     request: Request,
#     name: str = Form(...),
#     db: db_Session = Depends(get_db)
# ):
#     """Crea una nueva sesión y redirige al listado."""
#     errors = {}

#     # Validaciones básicas
#     if not name.strip():
#         errors["name"] = "El nombre no puede estar vacío."

#     existing = db.query(Session).filter(Session.name == name).first()
#     if existing:
#         errors["name"] = "Ya existe una sesión con ese nombre."

#     if errors:
#         return templates.TemplateResponse(
#             "session_form.html",
#             {
#                 "request": request,
#                 "form_data": {"name": name},
#                 "errors": errors,
#                 "action_url": "/sessions/new",
#             }
#         )

#     # Crear y guardar sesión
#     session = Session(name=name)
#     db.add(session)
#     db.commit()
#     db.refresh(session)

#     return RedirectResponse(url="/sessions", status_code=status.HTTP_303_SEE_OTHER)


# #ver detalles o editar una sesión
# @router.get("/{session_id}", response_class=HTMLResponse)
# def get_session(request: Request, session_id: int, db: db_Session = Depends(get_db)):
#     """Muestra los detalles de una sesión específica."""
#     session = db.query(Session).filter_by(id=session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Sesión no encontrada")

#     return templates.TemplateResponse(
#         "session_form.html",
#         {
#             "request": request,
#             "form_data": {"name": session.name},
#             "session": session,
#             "errors": {},
#             "action_url": f"/sessions/{session_id}",
#         }
#     )


# #actualizar sesión existente
# @router.put("/{session_id}")
# def update_session(
#     request: Request,
#     session_id: int,
#     name: str = Form(...),
#     db: db_Session = Depends(get_db)
# ):
#     """Actualiza el nombre de una sesión existente."""
#     session = db.query(Session).filter_by(id=session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Sesión no encontrada")

#     if not name.strip():
#         return templates.TemplateResponse(
#             "session_form.html",
#             {
#                 "request": request,
#                 "form_data": {"name": name},
#                 "errors": {"name": "El nombre no puede estar vacío."},
#                 "action_url": f"/sessions/{session_id}",
#                 "session": session,
#             }
#         )

#     # Validar duplicados
#     duplicate = db.query(Session).filter(Session.name == name, Session.id != session_id).first()
#     if duplicate:
#         return templates.TemplateResponse(
#             "session_form.html",
#             {
#                 "request": request,
#                 "form_data": {"name": name},
#                 "errors": {"name": "Ya existe otra sesión con ese nombre."},
#                 "action_url": f"/sessions/{session_id}",
#                 "session": session,
#             }
#         )

#     # Actualizar registro
#     session.name = name
#     db.commit()
#     db.refresh(session)

#     return RedirectResponse(url="/sessions", status_code=status.HTTP_303_SEE_OTHER)

# @router.post("/{session_id}/add_exercise")
# def add_exercise(
#     session_id: int,
#     name: str = Form(...),
#     db: db_Session = Depends(get_db)
# ):
#     session = db.query(Session).filter_by(id=session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Sesión no encontrada")

#     if not name.strip():
#         raise HTTPException(status_code=400, detail="El nombre del ejercicio no puede estar vacío")

#     from app.models.fitness import Exercise
#     exercise = Exercise(name=name, session_id=session.id)
#     db.add(exercise)
#     db.commit()
#     db.refresh(session)
#     return RedirectResponse(url=f"/sessions/{session_id}", status_code=status.HTTP_303_SEE_OTHER)

# #eliminar sesión
# @router.post("/{session_id}/delete")
# def delete_session(session_id: int, db: db_Session = Depends(get_db)):
#     """Elimina una sesión y redirige al listado."""
#     session = db.query(Session).filter_by(id=session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Sesión no encontrada")

#     db.delete(session)
#     db.commit()

#     return RedirectResponse(url="/sessions", status_code=status.HTTP_303_SEE_OTHER)
