import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.security import create_access_token

from main import app
from app.db.session import Base
from app.api.dependencies import get_db

client = TestClient(app)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    """Devuelve un cliente de pruebas FastAPI."""
    return TestClient(app)

@pytest.fixture
def create_user(test_client):
    def _create_user(username: str, email: str, password: str = "password123"):
        response = test_client.post(
            "/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=False
        )
        # Debe devolver 303 (redirect) si fue exitoso
        assert response.status_code in (200, 303), response.text
        return response
    return _create_user


@pytest.fixture
def login_user(test_client):
    def _login_user(username_or_email: str, password: str = "password123"):
        response = test_client.post(
            "/",
            data={"username_or_email": username_or_email, "password": password},
            follow_redirects=False
        )
        assert response.status_code in (200, 303), response.text
        token = response.cookies.get("access_token")
        assert token, f"No se recibió token para {username_or_email}"
        return {"Authorization": f"Bearer {token}"}
    return _login_user


@pytest.fixture
def auth_headers(test_client):
    def _auth_headers(username: str, email: str, password: str = "password123"):
        # Crear usuario
        response = test_client.post(
            "/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": password,
            }
        )
        assert response.status_code in (200, 201), response.text

        # Crear token válido (mismo SECRET_KEY y estructura)
        token = create_access_token({"sub": email})
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers


@pytest.fixture
def base_exercises():
    """Devuelve una lista base de ejercicios para usar en las rutinas.
    """
    return [
        {"exercise_name": "Press de pecho", "target_sets": 4, "target_reps": 10, "weight": 60},
        {"exercise_name": "Press militar", "target_sets": 3, "target_reps": 8, "weight": 40},
        {"exercise_name": "Remo con barra", "target_sets": 4, "target_reps": 10, "weight": 50},
        {"exercise_name": "Dominadas", "target_sets": 3, "target_reps": 8, "weight": 0},
        {"exercise_name": "Sentadilla", "target_sets": 4, "target_reps": 10, "weight": 80},
        {"exercise_name": "Peso muerto", "target_sets": 3, "target_reps": 8, "weight": 100}
    ]

@pytest.fixture
def create_routine(test_client, auth_headers, base_exercises):
    def _create_routine(username="user_a", email="a@example.com", routine_name="Rutina fuerza"):
        headers = auth_headers(username, email)
        payload = {
            "name": routine_name,
            "sessions": [
                {
                    "session_name": "Día 1 - Tren inferior",
                    "exercises": [b_e for b_e in base_exercises[:4]]
                },
                {
                    "session_name": "Día 2 - Tren superior",
                    "exercises": [b_e for b_e in base_exercises[4:]]
                }
            ]
        }
        response = test_client.post("/routines/", json=payload, headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        return data, headers
    return _create_routine

def test_create_routine_with_auth(create_routine):
    data, _ = create_routine()
    assert data["name"] == "Rutina fuerza"
    assert len(data["sessions"]) == 2

def test_edit_session_add_exercise(test_client, create_routine):
    routine, headers = create_routine("edit_user", "edit@example.com")
    import pdb; pdb.set_trace()
    session_id = routine["sessions"][0]["id"]
    print(test_client.app.routes)
    new_exercise = {"name": "Curl de bíceps", "sets": 3, "reps": 12, "weight": 15}
    update_data = {"exercises": [new_exercise]}

    response = test_client.put(f"/sessions/{session_id}", json=update_data, headers=headers)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert any(ex["name"] == "Curl de bíceps" for ex in updated["exercises"])