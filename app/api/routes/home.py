from fastapi import APIRouter, Form, HTTPException, Request, status, Depends
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from app.services.user_services import UserService
from app.schemas.user import TokenResponse
from app.services.auth_service import authenticate_user
from app.core.security import create_access_token
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Home"])
user_service = UserService()
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse(
                                    request,
                                    "register.html", 
                                        {
                                        "form_data": {}, 
                                        "errors": {}
                                        }
                                    )


@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    errors = {}
    form_data = {"username": username, "email": email} # Para repoblar el form si falla

    if password != confirm_password:
        errors["password"] = "Las contraseñas no coinciden"
    
    try:
        EmailStr._validate(email)
    except ValueError:
        errors["email"] = "El email no tiene un formato válido"

    try:
       user_service.validate_unique_user(db, username, email)
    except ValueError as e:
         errors["username"] = str(e)

    if errors:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"errors": errors,
             "form_data": {"username": username, "email": email}}
        )
    
    user_service.create_user(db, username, email, password)
    
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@router.post("/")
async def login_post(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
    ):

    user = authenticate_user(db, username_or_email, password)
    
    try:
        token = user_service.login(db, username_or_email, password)
    except ValueError as e:
        # Si falla, renderiza la plantilla de login con el error
        return templates.TemplateResponse(request, "login.html", {
            "error": str(e)
        })
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    """
    Página principal del usuario después de iniciar sesión.
    """
    return templates.TemplateResponse(request, "dashboard.html", {
        "username": current_user.username 
    })



# @router.get("/me", response_model=UserProfileResponse)
# def read_me(token: TokenResponse):
#     try:
#         user_profile_response = user_service.get_user_from_token(token)
#         return user_profile_response
#     except ValueError as e:
#         raise HTTPException(status_code=401, detail=str(e))