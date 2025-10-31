# app/models/user.py
from sqlalchemy import Column, Integer, String
from app.db.session import Base # Importa Base desde la nueva ubicación

# --- MODELOS AUTH ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)