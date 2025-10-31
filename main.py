# Librerias
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# --- INICIALIZACION ---

# Modulos propios
from app.models import user, fitness 
from app.db.session import SessionLocal, engine, Base 
from app.api.dependencies import get_db
from app.routes import users, home
from app.schemas import Exercise, ExerciseCreate # Debes importar los schemas para los endpoints


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

app.include_router(home.router, prefix="/home", tags=["Home"])  # login, /me
app.include_router(users.router, prefix="/users", tags=["Users"])  # backoffice

### --- ENDPOINTS ---


## PRUEBA DE USO DE LA BASE DE DATOS -) CARGAR Y LEER EJERCICIOS
@app.post("/exercises/", response_model=Exercise)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    # Check if an exercise with this name already exists
    db_exercise = (
        db.query(Exercise).filter(Exercise.name == exercise.name).first()
    )
    if db_exercise:
        raise HTTPException(
            status_code=400, detail="Exercise with this name already exists"
        )

    # Create the SQLAlchemy model instance
    db_exercise = Exercise(
        name=exercise.name,
        primary_muscles=exercise.primary_muscles,
        secondary_muscles=exercise.secondary_muscles,
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@app.get("/exercises/", response_model=List[Exercise])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = db.query(Exercise).offset(skip).limit(limit).all()
    return exercises


@app.get("/exercises/{exercise_id}", response_model=Exercise)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = (
        db.query(Exercise).filter(Exercise.id == exercise_id).first()
    )
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise
