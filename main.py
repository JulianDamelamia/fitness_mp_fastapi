# Librerias
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import users, home

# --- INICIALIZACION ---

# Modulos propios
from app import models, schemas
from app.db.session import SessionLocal, engine
from app.api.dependencies import get_db
from app.db.session import Base

# Crear las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)


# inicializar la aplicacion FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# para desp usar CSS/js externo
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router, prefix="", tags=["Home"])  # login, /me
app.include_router(users.router, prefix="/users", tags=["Users"])  # backoffice

### --- ENDPOINTS ---


## PRUEBA DE USO DE LA BASE DE DATOS -) CARGAR Y LEER EJERCICIOS
@app.post("/exercises/", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    # Check if an exercise with this name already exists
    db_exercise = (
        db.query(models.Exercise).filter(models.Exercise.name == exercise.name).first()
    )
    if db_exercise:
        raise HTTPException(
            status_code=400, detail="Exercise with this name already exists"
        )

    # Create the SQLAlchemy model instance
    db_exercise = models.Exercise(
        name=exercise.name,
        primary_muscles=exercise.primary_muscles,
        secondary_muscles=exercise.secondary_muscles,
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@app.get("/exercises/", response_model=List[schemas.Exercise])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = db.query(models.Exercise).offset(skip).limit(limit).all()
    return exercises


@app.get("/exercises/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = (
        db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    )
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise
