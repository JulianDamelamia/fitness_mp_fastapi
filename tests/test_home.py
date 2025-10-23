import pytest
from fastapi.testclient import TestClient
from main import app
from app.db import fake_user_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Se ejecuta antes y después de cada test para limpiar la base de datos"""
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register_login():
    '''me registro y logueo'''
    response = client.post(
        "/home/register",
        data={"username": "julian", "password": "notengoventanas"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "julian"

    response = client.post(
        "/home/login",
        data={"username": "julian", "password": "notengoventanas"}
    )
    assert response.status_code == 200
    login_data = response.json()
    assert "access_token" in login_data

