from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import SessionLocal, engine
from app.models.user import User
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user_services import UserService

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request):
    """Obtiene el usuario actualmente autenticado a partir del request HTTP.
    Return:
    - Objeto usuario correspondiente al correo extraído del token.
    Excepciones:
    - HTTPException(status_code=401): cuando no hay token, el token es inválido o
        el token ha expirado.
    Dependencias externas:
    - jwt.decode, SECRET_KEY, ALGORITHM, JWTError, user_service.get_user_by_email.
    """
    user_service = UserService()
    token = None
    # Prioridad: cookie → header
    if "access_token" in request.cookies:
        token = request.cookies.get("access_token")
    elif "Authorization" in request.headers:
        auth_header = request.headers.get("Authorization")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Token no encontrado. Iniciá sesión nuevamente.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido o expirado.")

        return user_service.get_user_by_email(email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")