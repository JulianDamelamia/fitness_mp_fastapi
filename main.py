
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from app.db.session import SessionLocal, engine, Base 
from app.api.dependencies import get_db, get_current_user
from app.api.routes import home, plans, users, routines
from app.schemas.fitness import ExerciseBase, ExerciseCreate, ExerciseResponse
from app.schemas import Exercise, ExerciseCreate
from app.services.user_services import UserService
from app.models.user import User, UserRole

# borrar tablas, util para desarrollo
# print("Borrando todas las tablas y recreando...")
# models.Base.metadata.drop_all(bind=engine)

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



app.include_router(home.router, tags=["Home"]) #Saqué prefijo home
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(routines.router, prefix="/routines", tags=["Routines"])
app.include_router(plans.router, prefix="/plans", tags=["Plans & Purchases"])

### --- ENDPOINTS ---


## PRUEBA DE USO DE LA BASE DE DATOS -) CARGAR Y LEER EJERCICIOS
@app.post("/exercises/", response_model=ExerciseBase)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    # Check if an exercise with this name already exists
    db_exercise = (
        db.query(ExerciseBase).filter(ExerciseBase.name == exercise.name).first()
    )
    if db_exercise:
        raise HTTPException(
            status_code=400, detail="Exercise with this name already exists"
        )

    # Create the SQLAlchemy model instance
    db_exercise = ExerciseBase(
        name=exercise.name,
        primary_muscles=exercise.primary_muscles,
        secondary_muscles=exercise.secondary_muscles,
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@app.get("/exercises/", response_model=List[ExerciseBase])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = db.query(ExerciseBase).offset(skip).limit(limit).all()
    return exercises


@app.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = (
        db.query(ExerciseBase).filter(ExerciseBase.id == exercise_id).first()
    )
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise


