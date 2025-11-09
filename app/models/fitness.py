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
    """attrs:
    id:int not_null
    name: str not_null
    creator_id: int FK users.id not_null

    creator: User
    plans: Plan
    sessions: [Session]
    """
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
    """attrs:
    id: int not_null
    session_name: str not_null
    routines: [Routine]
    exercises: [Exercise]
    session_logs: [SessionLog]
    """
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index = True)
    session_name = Column(String, nullable=False)

    routines = relationship(
        'Routine',
        secondary=routines_sessions,
        back_populates='sessions'
    )
    exercises = relationship('Exercise', back_populates='session')
    session_logs = relationship('SessionLog', back_populates='session', cascade="all, delete-orphan")
    



# Ejercicio como elemento abstracto que compone las sesiones
class Exercise(Base):
    """attrs:
    id: int not_null
    session_id: int FK sessions.id not_null
    exercise_name: str not_null
    target_sets: int not_null
    target_reps: int not_null
    target_weight: float nullable
    primary_muscles: JSON not_null
    secondary_muscles: JSON not_null
    logs: [ExerciseLog]
    """
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    exercise_name = Column(String)
    target_sets = Column(Integer)
    target_reps = Column(Integer)
    target_weight = Column(Float, nullable=True)

    session = relationship("Session", back_populates="exercises")

    primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
    secondary_muscles = Column(JSON) # e.g., ["hombros"]
    logs = relationship("ExerciseLog",back_populates='exercise')