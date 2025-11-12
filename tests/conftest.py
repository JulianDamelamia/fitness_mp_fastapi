import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.user import User
from app.models.fitness import Routine, Session, Exercise
from app.models.business import Plan, Purchase
from app.models.tracker import SessionLog, ExerciseLog
from app.models.associations import routines_sessions, plans_routines

from main import app as fastapi_app 
from app.api.dependencies import get_db

# --- Configuración de la Base de Datos de Prueba ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos limpia para cada test."""
    connection = engine.connect()
    Base.metadata.create_all(bind=connection)
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=connection)
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Crea un cliente de prueba que usa nuestra DB en memoria."""
    def override_get_db():
            yield db_session

    # Usamos el alias 'fastapi_app'
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(fastapi_app)

    # Usamos el alias 'fastapi_app' aquí también
    fastapi_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def authenticated_client(client):
    """Crea un cliente ya logueado con un usuario de prueba."""
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )

    client.post(
        "/login",
        data={"username_or_email": "testuser", "password": "password"},
    )
    
    yield client