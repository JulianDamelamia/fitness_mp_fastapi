import pytest
from app.auth import authenticate_user
from fastapi.testclient import TestClient
from main import app
from app.db import fake_user_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Se ejecuta antes y después de cada test para limpiar la DB."""
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register():
    '''me registro'''
    response = client.post(
                            "/home/register",
                            data={
                                "username": "julian", 
                                "password": "notengoventanas",
                                "full_name": "yo, julián",
                                "email": "julian@example.com"
                                }

                        )
    
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "julian"
    assert data["email"] == "julian@example.com"
    assert data["full_name"] == "yo, julián"
    assert "message" in data

def test_login_with_username_and_email():
    response = client.post(
                            "/home/register",
                            data={
                                "username": "julian", 
                                "password": "notengoventanas",
                                "full_name": "yo, julián",
                                "email": "julian@example.com"
                                }

                        )
    
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "julian"
    assert data["email"] == "julian@example.com"
    assert data["full_name"] == "yo, julián"
    assert "message" in data

    # login username
    response_login_user = client.post(
                                    "/home/login",
                                    data={
                                        "username_or_email": "julian", 
                                        "password": "notengoventanas"
                                        }
                                    )   
    assert response_login_user.status_code == 200
    token_user = response_login_user.json()["access_token"]
    assert token_user  # tiene que devolver token
    # login email
    response_login_email = client.post(
                                        "/home/login",
                                        data={
                                             "username_or_email": "julian@example.com",
                                            "password": "notengoventanas"
                                        }
                                    )

    assert response_login_email.status_code == 200
    token_email = response_login_email.json()["access_token"]
    assert token_email  # tiene que devolver token

    # # Probar endpoint protegido con token
    # response_me_user = client.get(
    #     "/home/me",
    #     headers={"Authorization": f"Bearer {token_user}"}
    # )
    # assert response_me_user.status_code == 200
    # assert response_me_user.json()["username"] == "julian"

    # response_me_email = client.get(
    #     "/home/me",
    #     headers={"Authorization": f"Bearer {token_email}"}
    # )
    # assert response_me_email.status_code == 200
    # assert response_me_email.json()["username"] == "julian"