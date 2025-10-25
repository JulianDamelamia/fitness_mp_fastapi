# Librerias
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import users, home

# Modulos propios
from app import models, schemas
from app.database import SessionLocal, engine

# Crear las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# inicializar la aplicacion FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# para desp usar CSS/js externo
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router, prefix="", tags=["Home"])  # login, /me
app.include_router(users.router, prefix="/users", tags=["Users"])  # backoffice

# --- ENDPOINTS ---
