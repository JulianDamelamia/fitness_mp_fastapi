import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.session import fake_user_db
from app.api.routes import users
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Se ejecuta antes y después de cada test para limpiar la DB."""
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register_and_delete_user():
    '''Me registro y luego elimino el usuario'''
    response = client.post(
                            "/users/register",
                            data={
                                "username": "julian",
                                "password": "notengoventanas"
                                }
                            )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "julian"

    response = client.delete("/users/julian")
    assert response.status_code == 200

