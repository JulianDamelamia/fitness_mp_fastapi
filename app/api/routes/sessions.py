from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.fitness import Session as FitnessSession
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def list_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(FitnessSession).filter(FitnessSession.creator_id == current_user.id).all()
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions})

@router.get("/new", response_class=HTMLResponse)
def create_session_form(request: Request):
    # Mostramos el formulario
    return templates.TemplateResponse("session_form.html", {"request": request})

@router.post("/new")
def create_session(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Creamos la sesión básica
    new_session = FitnessSession(session_name=name, creator_id=current_user.id)
    db.add(new_session)
    db.commit()
    return RedirectResponse(url="/sessions", status_code=303)