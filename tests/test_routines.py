import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app  
from app.db.session import Base  
from app.models.fitness import Routine, Session, Exercise
from app.api.dependencies import get_db
from app.services.routine_service import RoutineService
# ------------------------------------------------------------
# Configuración del entorno de prueba
# ------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_routines.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Borra y recrea todas las tablas antes de cada test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Devuelve una sesión de base de datos aislada."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def override_get_db():
    """Usa una base de datos temporal en cada test"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.rollback()
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------

@pytest.fixture
def seed_data():
    data_1 = {
        "name": "Rutina A - Push",
        "sessions": [
            {
                "session_name": "Día 1 - Empuje",
                "exercises": [
                    {"exercise_name": "Press banca", "target_sets": 4, "target_reps": 8},
                    {"exercise_name": "Press militar", "target_sets": 3, "target_reps": 10},
                ],
            }
        ],
    }

    data_2 = {
        "name": "Rutina B - Pull",
        "sessions": [
            {
                "session_name": "Día 2 - Espalda",
                "exercises": [
                    {"exercise_name": "Dominadas", "target_sets": 4, "target_reps": 6},
                    {"exercise_name": "Remo con barra", "target_sets": 3, "target_reps": 10},
                ],
            }
        ],
    }
    yield (data_1, data_2)


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_list_routines_empty():
    response = client.get("/routines/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_routine_with_new_session(seed_data):
    payload = seed_data[0]
    response = client.post("/routines/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rutina A - Push"
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["session_name"] == "Día 1 - Empuje"


def test_get_routine_by_id(seed_data):
    created = client.post("/routines/", json=seed_data[0])
    print(created.text)
    routine_id = created.json()["id"]
    response = client.get(f"/routines/{routine_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == routine_id
    assert data["name"] == "Rutina A - Push"


def test_update_routine_name_only(seed_data):
    payload = seed_data[1]
    routine = client.post("/routines/", json=payload).json()
    update_payload = {"name": "Rutina actualizada", "sessions": []}
    response = client.patch(f"/routines/{routine['id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rutina actualizada"


def test_create_routine_and_add_session(seed_data):
    """Crear rutina y luego agregar una nueva sesión sin sobrescribir"""
    # Crear rutina base
    base_payload = seed_data[0]
    response = client.post("/routines/", json=base_payload)
    assert response.status_code == 200
    routine = response.json()
    assert len(routine["sessions"]) == 1

    # Agregar una nueva sesión
    update_payload = seed_data[1]
    patch = client.patch(f"/routines/{routine['id']}", json=update_payload)
    assert patch.status_code == 200
    updated = patch.json()

    assert updated["name"] == "Rutina B - Pull"  # se actualiza el nombre
    assert len(updated["sessions"]) == 2  # la sesión nueva se agrega


def test_multiple_updates_are_additive(seed_data):
    """Aplicar dos actualizaciones seguidas y conservar todas las sesiones"""
    response = client.post("/routines/", json=seed_data[0])
    assert response.status_code == 200
    routine = response.json()

    for update in seed_data[1:]:
        patch = client.patch(f"/routines/{routine['id']}", json=update)
        assert patch.status_code == 200
        routine = patch.json()

    assert len(routine["sessions"]) == 2
    session_names = [s["session_name"] for s in routine["sessions"]]
    assert "Día 1 - Empuje" in session_names
    assert "Día 2 - Espalda" in session_names

def test_delete_routine():
    payload ={
        "name": "Rutina a borrar",
        "sessions": [
            {
                "session_name": "Día 2 - Pierna",
                "exercises": [
                    {"exercise_name": "Sentadilla", "target_sets": 5, "target_reps": 5}
                ],
            }
        ],
    }
    routine = client.post("/routines/", json=payload).json()
    rid = routine["id"]

    response = client.delete(f"/routines/{rid}")
    assert response.status_code in (200, 303, 307)

    response = client.get(f"/routines/{rid}")
    assert response.status_code == 404


def test_create_routine_with_invalid_payload():
    payload = {"nombre": "No válido"}  # mal key
    response = client.post("/routines/", json=payload)
    assert response.status_code == 422  # error de validación de FastAPI
