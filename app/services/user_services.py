from app.db.session import fake_user_db # <- Temporalmente para no romper el código dependiente
from app.core.security import hash_password, create_access_token
from app.schemas import UserProfileResponse, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user

class UserService:
    def __init__(self):
        self.db = fake_user_db

    def validate_unique_user(self, username:str, email:str):
        if username in self.db or any(u["email"] == email for u in self.db.values()):
            return False
        return True
    
    
    def create_user(self, username:str, email:str, password:str):
        if not self.validate_unique_user(username, email):
            raise ValueError("Usuario o email ya existe")

        hashed_password = hash_password(password)
        user_id = len(fake_user_db) + 1
        self.db[username] = {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password
        }
        
        return UserProfileResponse(
            id=user_id,
            username = username,
            email=email,
            message="Usuario registrado exitosamente"
        )

    def login(self, username_or_email, password):
        user = authenticate_user(username_or_email, password)
        if not user:
            raise ValueError('usuario o contraseña incorrectos')
        token = create_access_token({"sub": user["username"]})
        return TokenResponse(access_token=token, token_type="bearer")

