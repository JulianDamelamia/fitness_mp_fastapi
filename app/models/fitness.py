# app/models/fitness.py
from app.db.session import Base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, Text, Float,DateTime, Table
from sqlalchemy.orm import relationship
from app.models.associations import routines_sessions, plans_routines
# Formato:
# class NombreSingular(Base):
#   __tablename__ = 'nombre_plural'
# atributo = Column()
# relacion = relationship('ObjetoDestino', back_populates='relacion_destino')

class Routine(Base):
    __tablename__= "routines"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    creator = relationship("User", back_populates='created_routines')
    plans = relationship(
        'Plan',
        secondary=plans_routines,
        back_populates='routines'
    )
    sessions = relationship(
        'Session',
        secondary = routines_sessions,
        back_populates='routines')


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)

    routines = relationship(
        'Routine',
        secondary=routines_sessions,
        back_populates='sessions'
    )
    exercises = relationship('Exercise', back_populates='session')


# Ejercicio como elemento abstracto que compone las sesiones
class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    name = Column(String)
    target_sets = Column(Integer)
    target_reps = Column(Integer)
    target_weight = Column(Float, nullable=True)

    session = relationship("Session", back_populates="exercises")

    primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
    secondary_muscles = Column(JSON) # e.g., ["hombros"]
    logs = relationship("ExerciseLog",back_populates='exercise')