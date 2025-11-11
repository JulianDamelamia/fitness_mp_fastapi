import pytest
from fastapi.testclient import TestClient
from app.models.user import User

def test_register_user_successfully(client, db_session):
    """
    Prueba que un usuario puede registrarse y es redirigido a /login.
    """
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword",
            "confirm_password": "newpassword",
        },
        follow_redirects=False
    )
    
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    # Verificación en la base de datos
    user = db_session.query(User).filter_by(username="newuser").first()
    assert user is not None
    assert user.email == "new@example.com"

def test_login_successfully_redirects(client, db_session):
    """
    Prueba que un usuario puede registrarse, iniciar sesión y ser redirigido.
    """
    # Registrar usuario (como no tenemos authenticated_client, lo hacemos manual)
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )

    # Iniciar sesión
    response_login = client.post(
        "/login",
        data={"username_or_email": "testuser", "password": "password"},
        follow_redirects=False
    )
    
    assert response_login.status_code == 303
    assert response_login.headers["location"] == "/dashboard"

    response_dashboard = client.get("/dashboard")
    
    assert response_dashboard.status_code == 200
    assert "¡Bienvenido, testuser!" in response_dashboard.text