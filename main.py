
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from app.db.session import SessionLocal, engine, Base 
from app.api.dependencies import get_db, get_current_user

from app.api.routes import home, plans, users, routines, exercises, sessions

from app.services.user_services import UserService 
from app.models.user import User, UserRole

from app.schemas.fitness import ExerciseBase, ExerciseCreate, ExerciseResponse

# Crear las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)


# --- PROMUEVE UN USUARIO EXISTENTE A ADMIN (SOLO SI NO HAY ADMIN) ---
def promote_user_to_admin(username_to_promote: str):
    db = SessionLocal()
    try:
        # Buscar si ya existe un admin
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_user:
            print(f"El usuario '{admin_user.username}' ya es administrador. Omitiendo promoción.")
            return

        # Si no hay admin, buscar al usuario que queremos promover
        user_to_promote = db.query(User).filter(User.username == username_to_promote).first()
        
        if user_to_promote:
            # 3. Promover al usuario
            user_to_promote.role = UserRole.ADMIN
            db.commit()
            print(f"¡Usuario '{username_to_promote}' promovido a ADMIN exitosamente!")
        else:
            # 4. No se encontró al usuario
            print(f"Error: No se encontró al usuario '{username_to_promote}' para promoverlo.")
            
    except Exception as e:
        print(f"Ocurrió un error al promover el admin: {e}")
        db.rollback() # Revertir cambios si algo falla
    finally:
        db.close() # Siempre cerrar la sesión


promote_user_to_admin("nico")

# inicializar la aplicacion FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# para desp usar CSS/js externo
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

## levantar la app con 
# DEBUG=1 uvicorn main:app --reload
if os.getenv("DEBUG") == "1":
    from app.schemas.user import UserResponse
    def fake_current_user():
        # Devuelve un "usuario" simulado
        return UserResponse(
                    id=999,
                    username="dev_user",
                    email="dev_user@example.com",
                    message="Usuario encontrado exitosamente"
                ) 

    app.dependency_overrides[get_current_user] = fake_current_user
    print("⚠️  Modo desarrollador activo: autenticación desactivada.")


# --- Registro de Routers ---
app.include_router(home.router, tags=["Home"]) #Saqué prefijo home
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(routines.router, prefix="/routines", tags=["Routines"])
app.include_router(plans.router, prefix="/plans", tags=["Plans & Purchases"])
app.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])