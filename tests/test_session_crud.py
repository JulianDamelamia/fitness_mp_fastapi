import pytest
from datetime import date, timezone, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, SessionLog
from app.schemas.session import CreateSessionSchema, ExerciseInSession
from app.builders.session_factory import SessionFactory
from app.models.fitness import Exercise, Session as fitnessSession
from app.models.tracker import SessionLog, ExerciseLog


# --- FIXTURE DE BD EN MEMORIA ---
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


# --- TEST 1: Crear una sesión ---
def test_create_session_with_exercises(session):
    s = fitnessSession(name='Push Day')
    session.add(s)
    session.commit()
    session.refresh(s)

    e1 = Exercise(name='press pecho') #estaría bueno tener una base de datos mock con ejercicios, sesiones y rutinas para testear
    e2= Exercise(name='press militar')
    session.add_all([e1, e2])
    session.commit()
    session.refresh(e1)
    session.refresh(e2)

    data = CreateSessionSchema(
        session_id =s.id,
        date=datetime.now(timezone.utc).date(),
        exercises=[
            ExerciseInSession(exercise_id=e1.id, weight=80, reps=[10, 8, 8]),
            ExerciseInSession(exercise_id=e2.id, weight=40, reps=[12, 10, 8])
        ],
    )

    factory = SessionFactory(session)
    session_log = factory.create_session(data)

    session.add(session_log)
    session.commit()
    session.refresh(session_log)

    print("\n=== SessionLog persistido ===")
    print("ID:", session_log.id)
    print("Nombre:", session_log.session.name)
    print("Fecha:", session_log.date)

    print("\n=== Ejercicios logueados ===")
    for log in session_log.exercise_logs:
        print({
            "log_id": log.id,
            "exercise_name": log.exercise.name,
            "weight": log.weight,
            "reps": log.reps,
            "set_n": log.set_n
        })

    # Assertions básicos
    assert session_log.id is not None
    assert len(session_log.exercise_logs) == 2
    assert session_log.exercise_logs[0].exercise.name == "press pecho"
    assert session_log.exercise_logs[1].exercise.name == "press militar"


## --- TEST 2: Recuperar una sesión ---
# def test_retrieve_session_with_exercises(session):
#     Preparamos los datos "manualmente"
#     press = Exercise(name="Press banca")
#     military = Exercise(name="Press militar")
#     session.add_all([press, military])
#     session.commit()

#     session_log = SessionLog(name="Push Day", date=date(2025, 11, 5))
#     session.add(session_log)
#     session.commit()

#     log1 = ExerciseLog(exercise_id=press.id, weight=80, set_n=3)
#     log2 = ExerciseLog(exercise_id=military.id, weight=40, set_n=3)
#     session_log.exercise_logs.extend([log1, log2])
#     session.commit()

#     Recuperamos
#     recovered = session.query(SessionLog).first()
#     print("\n=== Sesión recuperada ===")
#     print("ID:", recovered.id)
#     print("Nombre:", recovered.name)
#     print("Fecha:", recovered.date)

#     print("\n=== Ejercicios recuperados ===")
#     for log in recovered.exercise_logs:
#         print({
#             "log_id": log.id,
#             "exercise_name": log.exercise.name,
#             "weight": log.weight,
#             "set_n": log.set_n
#         })

#     assert recovered.name == "Push Day"
#     assert len(recovered.exercise_logs) == 2
#     assert recovered.exercise_logs[0].exercise.name == "Press banca"
#     assert recovered.exercise_logs[1].exercise.name == "Press militar"
