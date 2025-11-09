from fastapi import APIRouter, Form, HTTPException, Request, status
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from app.services.user_services import UserService

router = APIRouter(tags=["Home"])
user_service = UserService()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse(
                                    "register.html", 
                                        {
                                        "request": request,
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
    confirm_password: str = Form(...)
    ):
    errors = {}

    if password != confirm_password:
        errors["password"] = "Las contraseñas no coinciden"
    
    try:
        EmailStr._validate(email)
    except ValueError:
        errors["email"] = "El email no tiene un formato válido"

    try:
       user_service.validate_unique_user(username, email)
    except ValueError as e:
         errors["username"] = str(e)

    if errors:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "errors": errors,
             "form_data": {"username": username, "email": email}}
        )
    user_service.create_user(username, email, password)
    return RedirectResponse(url="/", status_code=303)

@router.get("/", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/")
async def login_post(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...)
    ):
    try:
        token = user_service.login(username_or_email, password)
    except ValueError:
        return HTTPException(
                            status_code = status.HTTP_401_UNAUTHORIZED,
                            detail =  "usuario o contraseña inválidos"
                            )                
    response = RedirectResponse(url="/sessions/", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

# @router.get("/me", response_model=UserProfileResponse)
# def read_me(token: TokenResponse):
#     try:
#         user_profile_response = user_service.get_user_from_token(token)
#         return user_profile_response
#     except ValueError as e:
#         raise HTTPException(status_code=401, detail=str(e))