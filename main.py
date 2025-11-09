
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from app.db.session import SessionLocal, engine, Base 
from app.api.dependencies import get_db, get_current_user
from app.api.routes import home, plans, routines
from app.schemas import ExerciseBase, ExerciseCreate


# borrar tablas, util para desarrollo
# print("Borrando todas las tablas y recreando...")
# models.Base.metadata.drop_all(bind=engine)

# Crear las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)


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


app.include_router(home.router)  # login, /me
app.include_router(plans.router) 
app.include_router(routines.router) 




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


@app.get("/exercises/{exercise_id}", response_model=ExerciseBase)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = (
        db.query(ExerciseBase).filter(ExerciseBase.id == exercise_id).first()
    )
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise
