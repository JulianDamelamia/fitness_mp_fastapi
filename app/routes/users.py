from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from app.schemas import UserResponse
from app.auth import hash_password
from app.db import fake_user_db

router = APIRouter()

@router.get("/", response_model=list[str])
def list_users():
    return list(fake_user_db.keys())


@router.post("/register")
def register_form(username: str = Form(...), password: str = Form(...)):
    if username in fake_user_db:
        return JSONResponse(status_code=400, content={"detail": "Usuario ya existe"})
    hashed = hash_password(password)
    fake_user_db[username] = {"username": username, "hashed_password": hashed}
    return {"username": username, "message": "Usuario registrado"}

@router.delete("/{username}", response_model=UserResponse)
def delete_user(username: str):
    if username not in fake_user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    del fake_user_db[username]
    return UserResponse(username=username, message="Usuario eliminado exitosamente")
