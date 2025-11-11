"""
File: app/data/create_default_data.py

Populate test.db with a baseline set of exercises for testing.

This module targets an Exercise model with the following columns/relationships:
- id: Integer primary key
- session_id: Integer ForeignKey to sessions.id
- exercise_name: String (name of the exercise)
- target_sets: Integer
- target_reps: Integer
- target_weight: Float (nullable)
- primary_muscles: JSON (e.g. ["pectoralis", "triceps"])
- secondary_muscles: JSON (e.g. ["deltoids"])
- logs: relationship to ExerciseLog

Notes:
- DEFAULT_EXERCISES (declared below) should supply keys that match the model column names
    (exercise_name, session_id, target_sets, target_reps, target_weight, primary_muscles, secondary_muscles).
- The insertion routine will filter out any keys that are not actual model columns.
- Usage:
        inject_default_exercises("sqlite:///./test.db")
"""

from app.data.create_default_data import inject_default_exercises
from typing import Dict, List, Any
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# Import your ORM model(s) and (optionally) Base from your project
# This file expects a SQLAlchemy declarative model named `Exercise` in models.fitness
from models.fitness import Exercise  # type: ignore

try:
    # Base is optional; if present we can call create_all
    from models.fitness import Base  # type: ignore
except Exception:
    Base = None  # type: ignore


DEFAULT_EXERCISES: List[Dict[str, Any]] = [
    {
        "exercise_name": "Push Up",
        "session_id": 1,
        "target_sets": 3,
        "target_reps": 12,
        "target_weight": None,
        "primary_muscles": ["pectoralis"],
        "secondary_muscles": ["triceps", "anterior_deltoid"],
    },
    {
        "exercise_name": "Squat",
        "session_id": 1,
        "target_sets": 4,
        "target_reps": 8,
        "target_weight": None,
        "primary_muscles": ["quadriceps"],
        "secondary_muscles": ["glutes", "hamstrings"],
    },
    {
        "exercise_name": "Pull Up",
        "session_id": 1,
        "target_sets": 4,
        "target_reps": 6,
        "target_weight": None,
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps"],
    },
    {
        "exercise_name": "Plank",
        "session_id": 1,
        "target_sets": 3,
        "target_reps": 60,  # seconds stored as integer reps if that's how model is used
        "target_weight": None,
        "primary_muscles": ["rectus_abdominis"],
        "secondary_muscles": ["obliques", "transverse_abdominis"],
    },
    {
        "exercise_name": "Deadlift",
        "session_id": 1,
        "target_sets": 3,
        "target_reps": 5,
        "target_weight": None,
        "primary_muscles": ["glutes", "hamstrings"],
        "secondary_muscles": ["erector_spinae", "trapezius"],
    },
]


def inject_default_exercises(db_url: str = "sqlite:///test.db") -> None:
    """
    Insert default exercises into the database at db_url if they do not already exist.

    The function:
    - creates tables if a declarative Base is exposed in models.fitness
    - inspects Exercise.__table__ to determine valid columns
    - for each DEFAULT_EXERCISE, filters fields to valid columns and inserts if no existing
      exercise with the same name exists (if a 'name' column exists). If no 'name' column,
      it attempts to find an exact match on provided fields.

    Args:
        db_url: SQLAlchemy database URL (defaults to sqlite:///test.db)
    """
    engine = create_engine(
        db_url,
        connect_args=(
            {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        ),
    )
    SessionLocal = sessionmaker(bind=engine)

    # create tables if Base is available
    if Base is not None:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            # If Base doesn't actually correspond or create_all fails, continue and attempt inserts.
            pass

    # determine valid model columns
    try:
        columns = {col.name for col in Exercise.__table__.columns}
    except Exception as exc:
        raise RuntimeError("Could not inspect Exercise model table/columns.") from exc

    with SessionLocal() as session:
        try:
            for entry in DEFAULT_EXERCISES:
                # keep only keys that are actual columns on the model
                filtered = {k: v for k, v in entry.items() if k in columns}

                if not filtered:
                    # nothing to insert for this entry (no matching columns)
                    continue

                exists = None
                if "name" in columns and "name" in filtered:
                    exists = (
                        session.query(Exercise).filter_by(name=filtered["name"]).first()
                    )
                else:
                    # build a filter using all provided fields
                    q = session.query(Exercise)
                    for k, v in filtered.items():
                        q = q.filter(getattr(Exercise, k) == v)
                    exists = q.first()

                if exists:
                    # skip if already present
                    continue

                obj = Exercise(**filtered)
                session.add(obj)

            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise


# Optional convenience: run when executed directly
if __name__ == "__main__":
    # default path relative to project root: ./test.db
    db_path = os.environ.get("TEST_DB_URL", "sqlite:///./test.db")
    inject_default_exercises(db_path)
