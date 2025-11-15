"""
Rutas de la API para la gestión de ejercicios de fitness.
Proporciona endpoints para crear, leer y consultar ejercicios individuales.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.fitness import ExerciseCreate, ExerciseResponse
from app.models.fitness import Exercise

router = APIRouter()


@router.post("/", response_model=ExerciseResponse)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = (
        db.query(Exercise)
        .filter(Exercise.exercise_name == exercise.exercise_name)
        .first()
    )
    if db_exercise:
        raise HTTPException(
            status_code=400, detail="Exercise with this name already exists"
        )

    db_exercise = Exercise(
        exercise_name=exercise.exercise_name,
        target_sets=exercise.target_sets,
        target_reps=exercise.target_reps,
        target_weight=exercise.target_weight,
        primary_muscles=exercise.primary_muscles,
        secondary_muscles=exercise.secondary_muscles,
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.get("/", response_model=List[ExerciseResponse])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Exercise).offset(skip).limit(limit).all()


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise
