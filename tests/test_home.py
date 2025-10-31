import pytest
from app.services.auth_service import authenticate_user
from fastapi.testclient import TestClient
from main import app
from app.db.session import fake_user_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Se ejecuta antes y después de cada test para limpiar la DB."""
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register_exitoso(): # Nombre de función más claro
    '''me registro exitosamente'''
    # Se añade 'follow_redirects=False' y se espera '303'
    response = client.post(
                            "/home/register",
                            data={
                                "username": "julian", 
                                "password": "notengoventanas",
                                "confirm_password": "notengoventanas",
                                "email": "julian@example.com"
                                },
                            follow_redirects=False # Importante para obtener el 303
                        )
    
    # 1. El registro exitoso debe resultar en una redirección (303)
    assert response.status_code == 303
    # 2. Debe redirigir a /login
    assert response.headers["location"] == "/login"

    # Nota: No puedes chequear el JSON porque es una redirección, no un cuerpo de respuesta JSON.
    # El test de que el usuario se creó debe estar implícito en el test de login, o bien
    # tendrías que simular la dependencia de base de datos para verificarla directamente.
    
# El test de login debe registrar al usuario y luego loguearlo
def test_login_con_usuario_y_email_exitoso():
    # Paso 1: Registro (con redirección desactivada para verificar el 303)
    register_response = client.post(
                            "/home/register",
                            data={
                                "username": "julian", 
                                "password": "notengoventanas",
                                "confirm_password": "notengoventanas",
                                "email": "julian@example.com"
                                },
                            follow_redirects=False 
                        )
    
    assert register_response.status_code == 303
    
    # Paso 2: Login con username
    # Se espera 303 (redirección a /dashboard)
    response_login_user = client.post(
                                    "/home/login",
                                    data={
                                        "username_or_email": "julian", 
                                        "password": "notengoventanas"
                                        },
                                    follow_redirects=False # Importante
                                    )   
    # El login exitoso debe resultar en una redirección (303)
    assert response_login_user.status_code == 303
    assert response_login_user.headers["location"] == "/dashboard"
    # Debe haber un token en la cookie 'access_token'
    assert "access_token" in response_login_user.cookies

    # Paso 3: Login con email
    # Se espera 303 (redirección a /dashboard)
    response_login_email = client.post(
                                        "/home/login",
                                        data={
                                             "username_or_email": "julian@example.com",
                                            "password": "notengoventanas"
                                        },
                                        follow_redirects=False # Importante
                                    )

    assert response_login_email.status_code == 303
    assert response_login_email.headers["location"] == "/dashboard"
    # Debe haber un token en la cookie 'access_token'
    assert "access_token" in response_login_email.cookies
