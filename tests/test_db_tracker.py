"""Tests for the database models and relationships in the fitness tracking application."""

from datetime import date
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload

from app.db.session import Base
from app.models import Exercise, SessionLog, ExerciseLog


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_create_exercise(db):
    exercise = Exercise(exercise_name="press de pecho")
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    assert exercise.id is not None
    assert exercise.exercise_name == "press de pecho"


def test_create_session_log(db):
    session_log = SessionLog(date=date.today(), session_id=1, user_id=1)
    db.add(session_log)
    db.commit()
    db.refresh(session_log)

    assert session_log.id is not None
    assert session_log.session_id == 1
    assert session_log.user_id == 1


def test_exercise_log_relationship(db):
    # armo ejercicio
    exercise = Exercise(exercise_name="plimplimplom al fallo")
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    # armo log de la sesión
    session_log = SessionLog(date=date.today(), session_id=1, user_id=1)
    db.add(session_log)
    db.commit()
    db.refresh(session_log)

    # armo el log
    log = ExerciseLog(
        session_log_id=session_log.id,
        exercise_id=exercise.id,
        weight=100,
        reps=8,
        set_n=1,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    assert log.exercise.exercise_name == "plimplimplom al fallo"
    assert log.session_logs.id == session_log.id
    assert exercise.logs[0].weight == 100


def test_lazy_joined_load(db):
    exercise = Exercise(exercise_name="merequetengue")
    session_log = SessionLog(date=date.today(), session_id=2, user_id=2)
    db.add_all([exercise, session_log])
    db.commit()

    log = ExerciseLog(
        session_log_id=session_log.id,
        exercise_id=exercise.id,
        weight=120,
        reps=5,
        set_n=1,
    )
    db.add(log)
    db.commit()

    # joinedload debería traerme el ejercicio sin necesidad de un query extra
    result = db.query(ExerciseLog).options(joinedload(ExerciseLog.exercise)).first()

    assert result.exercise.exercise_name == "merequetengue"


def test_multiple_logs_same_exercise(db):
    exercise = Exercise(exercise_name="no levantar ni sospechas")
    session_log = SessionLog(date=date.today(), session_id=3, user_id=3)
    db.add_all([exercise, session_log])
    db.commit()

    logs = [
        ExerciseLog(
            session_log_id=session_log.id,
            exercise_id=exercise.id,
            weight=40,
            reps=10,
            set_n=1,
        ),
        ExerciseLog(
            session_log_id=session_log.id,
            exercise_id=exercise.id,
            weight=42.5,
            reps=8,
            set_n=2,
        ),
        ExerciseLog(
            session_log_id=session_log.id,
            exercise_id=exercise.id,
            weight=45,
            reps=6,
            set_n=3,
        ),
    ]
    db.add_all(logs)
    db.commit()

    assert len(exercise.logs) == 3
    assert exercise.logs[2].weight == 45
