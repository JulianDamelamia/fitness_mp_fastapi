from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# Importa las constantes de configuración desde el nuevo módulo
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Inicialización de contextos
# La inicialización del pwd_context se mantiene aquí porque es parte de la criptografía
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# El esquema OAuth2 también es parte de la seguridad/autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/home/login")


# --- FUNCIONES DE HASHING ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    # Necesitas importar verify_password y hash_password de la versión anterior
    # si no estaban en el extracto que me enviaste.
    return pwd_context.verify(password, hashed)


# --- FUNCIÓN DE JWT ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
