from app.db import fake_user_db
from app.auth import hash_password, verify_password, create_access_token,authenticate_user
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from app.schemas import UserProfileResponse, Token, UserResponse

class UserService:
    def __init__(self):
        self.db = fake_user_db

    def validate_unique_user(self, username:str, email:str):
        if username in self.db or any(u["email"] == email for u in self.db.values()):
            return False
        return True
    
    def create_user(self, username:str, password:str, full_name:str, email:str):
        if not self.validate_unique_user(username, email):
            raise ValueError("Usuario o email ya existe")

        hashed = hash_password(password)
        self.db[username] = {
            "username": username,
            "hashed_password": hashed,
            "full_name": full_name,
            "email": email
        }
        
        return UserProfileResponse(
            username=username,
            email=email,
            full_name=full_name,
            message="Usuario registrado exitosamente"
        )

    def login(self, username_or_email, password):
        # Buscar usuario
        user = authenticate_user(username_or_email, password)    
        token = create_access_token({"sub": user["username"]})
        return Token(access_token=token, token_type="bearer")

    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None or username not in self.db:
                raise ValueError("Token inválido")
            user = self.db[username]
            return UserProfileResponse(
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                message="Perfil obtenido correctamente"
            )
        except JWTError:
            raise ValueError("Token inválido")