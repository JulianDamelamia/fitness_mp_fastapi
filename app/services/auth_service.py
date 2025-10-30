from app.db.session import fake_user_db # <- Temporalmente para no romper el código dependiente
from app.core.security import verify_password, create_access_token # <- NUEVOS IMPORTS
from typing import Optional, Dict
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Esta función de acceso a datos (que idealmente iría en un Repository) se queda
# en el Servicio por ahora.
def authenticate_user(username_or_email:str, password:str):
    if not username_or_email or not password:
        return None
    # Esta lógica DEBE ser reemplazada por una consulta a la DB de SQLAlchemy.
    for user in fake_user_db.values():
        if (user["username"] == username_or_email or user["email"] == username_or_email) and verify_password(password, user["hashed_password"]):
            print("gr8 succes")
            return user
    return None