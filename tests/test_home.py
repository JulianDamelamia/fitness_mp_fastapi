"""Tests para la funcionalidad de registro"""

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
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    # Verificación en la base de datos
    user = db_session.query(User).filter_by(username="newuser").first()
    assert user is not None
    assert user.email == "new@example.com"
