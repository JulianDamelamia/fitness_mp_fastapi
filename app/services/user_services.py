"""Módulo que implementa servicios para gestionar usuarios en la aplicación de fitness."""

from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token
from app.services.auth_service import authenticate_user


class UserService:
    def __init__(self):
        pass

    def validate_unique_user(self, db: Session, username: str, email: str):
        user_by_username = db.query(User).filter(User.username == username).first()
        user_by_email = db.query(User).filter(User.email == email).first()
        if user_by_username or user_by_email:
            raise ValueError("Usuario o email ya existe")
        return True

    def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        password: str,
        is_pending_trainer: bool = False,
    ) -> User:

        hashed_password = hash_password(password)

        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,
            is_pending_trainer=is_pending_trainer,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    def login(self, db: Session, username_or_email, password):
        user = authenticate_user(db, username_or_email, password)
        if not user:
            raise ValueError("usuario o contraseña incorrectos")

        token_data = {"sub": user.username, "id": user.id}
        token = create_access_token(token_data)

        return token
