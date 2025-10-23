from fastapi import APIRouter, Form, HTTPException
from app.db import fake_user_db
from app.auth import hash_password, verify_password, create_access_token, authenticate_user
from app.schemas import UserResponse, Token, UserProfileResponse
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
router = APIRouter()


@router.post("/register", response_model=UserProfileResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...)
    ):
    if username in fake_user_db or any(u["email"] == email for u in fake_user_db.values()):
        raise HTTPException(status_code=400, detail="Usuario o email ya existe")
    hashed = hash_password(password)

    fake_user_db[username] = {"username": username, "hashed_password": hashed, "full_name": full_name, "email": email}
    return UserProfileResponse(username=username,email=email, full_name=full_name, message="Usuario registrado exitosamente")

@router.post("/login", response_model=Token)
def login_form(username_or_email: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username_or_email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse) #TODO
def read_me(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in fake_user_db:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = fake_user_db[username]
        return {**user, "message": "Perfil obtenido correctamente"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")