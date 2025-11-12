from app.db.session import SessionLocal
from app.core.security import verify_password, create_access_token # <- NUEVOS IMPORTS
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


#Autentica a un usuario contra la base de datos de SQLAlchemy. Retorna el objeto User si es exitoso, None si no.

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    
    if not username_or_email or not password:
        return None
    
    # Buscar al usuario por username o email en la DB
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    # Si no se encuentra el usuario o la contraseña no coincide
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # Autenticación exitosa
    return user