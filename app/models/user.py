# app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.business import Plan
from app.db.session import Base # Importa Base desde la nueva ubicación

# --- MODELOS AUTH ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)

    created_plans = relationship('Plan', back_populates='creator')
    created_routines = relationship('Routine', back_populates='creator')
