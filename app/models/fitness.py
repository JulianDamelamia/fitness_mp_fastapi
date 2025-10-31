# app/models/fitness.py
from sqlalchemy import Column, Integer, String, JSON
from app.db.session import Base # Importa Base desde la nueva ubicación

# --- MODELOS EJERCICIOS ---
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    
    # Usamos JSON para almacenar listas de músculos
    primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
    secondary_muscles = Column(JSON) # e.g., ["hombros"]