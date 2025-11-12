import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from sqlalchemy.orm import Session

def test_list_users(client, db_session):
    """
    Prueba que podemos listar usuarios después de crear uno.
    """
    # Preparación: Registrar un usuario
    client.post(
        "/register",
        data={
            "username": "user_to_list",
            "email": "list@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )
    
    # Acción: Llamar al endpoint de listar usuarios
    response = client.get("/users/")
    
    # Verificación
    assert response.status_code == 200
    data = response.json()
    assert "user_to_list" in data

def test_delete_user(client, db_session: Session):
    """
    Prueba que podemos registrar un usuario y luego eliminarlo.
    """
    # Preparación: Registrar el usuario a eliminar
    client.post(
        "/register",
        data={
            "username": "user_to_delete",
            "email": "delete@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )
    
    # Verificación de que existe en la DB
    user = db_session.query(User).filter_by(username="user_to_delete").first()
    assert user is not None

    # Acción: Llamar al endpoint de eliminar
    response = client.delete(f"/users/{user.username}")
    
    # Verificación de la respuesta
    assert response.status_code == 200
    assert response.json()["message"] == "Usuario eliminado exitosamente"
    
    # Verificación final en la DB (el usuario ya no debe estar)
    user_deleted = db_session.query(User).filter_by(username="user_to_delete").first()
    assert user_deleted is None
