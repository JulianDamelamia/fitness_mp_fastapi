from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, create_access_token
from app.schemas import UserProfileResponse, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user


class UserService:
    def __init__(self):
        pass

    def validate_unique_user(self, db: Session, username:str, email:str) -> bool:
        if db.query(User).filter(User.username == username).first():
            raise ValueError("El nombre de usuario ya existe")
        if db.query(User).filter(User.email == email).first():
            raise ValueError("El email ya está registrado")
        return True
    
    
    def create_user(self, db: Session, username: str, email: str, password: str) -> User:
        hashed_password = hash_password(password)
        
        # Crea la instancia del modelo SQLAlchemy
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user

    def login(self, db: Session, username_or_email, password):
        user = authenticate_user(db, username_or_email, password)
        if not user:
            raise ValueError('usuario o contraseña incorrectos')
        token = create_access_token({"sub": user["username"]})
        return TokenResponse(access_token=token, token_type="bearer")

    def get_user_by_email(self, email: str):
        for user in self.db.values():
            if user["email"] == email:
                return UserResponse(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    message="Usuario encontrado exitosamente"
                )
        return None
