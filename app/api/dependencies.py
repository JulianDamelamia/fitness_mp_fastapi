from app.db.session import SessionLocal
from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import User, UserRole
from app.core.security import oauth2_scheme

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_from_cookie(access_token: str | None = Cookie(None)) -> str | None:
    """
    Dependencia simple para extraer el token de la cookie 'access_token'
    """
    return access_token


def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodifica el token JWT y retorna el objeto User de la base de datos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user


def get_current_trainer(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia que valida que el usuario actual tenga el rol 'TRAINER'.
    """
    if current_user.role != UserRole.TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de entrenador para realizar esta acción"
        )
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia que valida que el usuario actual tenga el rol 'ADMIN'.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada solo para administradores"
        )
    return current_user