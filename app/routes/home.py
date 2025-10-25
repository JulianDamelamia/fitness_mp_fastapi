from fastapi import APIRouter, Form, HTTPException
from app.db import fake_user_db
from app.auth import hash_password, verify_password, create_access_token, authenticate_user
from app.schemas import UserResponse, Token, UserProfileResponse
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from app.services.user_services import UserService
router = APIRouter()
user_service = UserService()


@router.post("/register", response_model=UserProfileResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...)
    ):
    try:
        return user_service.create_user(username, password, full_name, email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_form(username_or_email: str = Form(...), password: str = Form(...)):
    try:
        token = user_service.login(username_or_email, password)
    except ValueError:
         raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return token

@router.get("/me", response_model=UserProfileResponse)
def read_me(token: Token):
    try:
        user_profile_response = user_service.get_user_from_token(token)
        return user_profile_response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))