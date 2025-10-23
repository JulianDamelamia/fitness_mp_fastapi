from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.db import fake_user_db
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register")
def register_form(username: str = Form(...), password: str = Form(...)):
    if username in fake_user_db:
        return JSONResponse(status_code=400, content={"detail": "Usuario ya existe"})
    hashed = hash_password(password)
    fake_user_db[username] = {"username": username, "hashed_password": hashed}
    return {"username": username, "message": "Usuario registrado"}

@router.post("/login")
def login_form(username: str = Form(...), password: str = Form(...)):
    user = fake_user_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return JSONResponse(status_code=400, content={"detail": "Usuario o contraseña incorrectos"})
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}