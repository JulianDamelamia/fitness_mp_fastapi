from sqlalchemy import Column, Integer, String, JSON
from app.db.session import Base


# --- MODELOS AUTH ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)


# --- MODELOS EJERCICIOS ---
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    
    # Usamos JSON para almacenar listas de músculos
    primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
    secondary_muscles = Column(JSON) # e.g., ["hombros"]