from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, Text, Float,DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base


# --- MODELOS AUTH ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)


# --- MODELOS EJERCICIOS --- (abstracto)
# class Exercise(Base):
#     __tablename__ = "exercises"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True, unique=True)
#     session_template_id = Column(Integer, ForeignKey("session_templates.id"))
    
#     # Usamos JSON para almacenar listas de músculos
#     primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
#     secondary_muscles = Column(JSON) # e.g., ["hombros"]

# planes
class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    price = Column(Integer)
    trainer_id = Column(Integer, ForeignKey("users.id"))

    routine = relationship("Routine", back_populates="plan")

# RUTINA
class Routine(Base):
    __tablename__= "routines"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    plan_id = Column(Integer, ForeignKey('plans.id'))

    plan = relationship("Plan", back_populates="routine")
    session_templates = relationship("SessionTemplate", back_populates="routine")   

# Sesión como elemento abstracto que compone las rutinas
class SessionTemplate(Base):
    __tablename__ = "session_templates"
    id = Column(Integer, primary_key=True)
    routine_id = Column(Integer, ForeignKey("routines.id"))
    name = Column(String)  # Ej: "Día 1 o PUSH"

    routine = relationship("Routine", back_populates="session_templates")
    exercises = relationship("ExerciseTemplate", back_populates="session_template")

# Ejercicio como elemento abstracto que compone las sesiones
class ExerciseTemplate(Base):
    __tablename__ = "exercise_templates"
    id = Column(Integer, primary_key=True)
    session_template_id = Column(Integer, ForeignKey("session_templates.id"))
    exercise_name = Column(String)
    target_sets = Column(Integer)
    target_reps = Column(Integer)
    target_weight = Column(Float, nullable=True)

    session_template = relationship("SessionTemplate", back_populates="exercises")

    primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
    secondary_muscles = Column(JSON) # e.g., ["hombros"]

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    purchase_date = Column(DateTime, default=datetime.now(timezone.utc))

    sessions = relationship("Session", back_populates="purchase")

# Sesión concreta realizada por el usuario
class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    session_template_id = Column(Integer, ForeignKey("session_templates.id"))
    date = Column(DateTime, default=datetime.now(timezone.utc))

    purchase = relationship("Purchase", back_populates="sessions")
    session_template = relationship("SessionTemplate")
    performed_exercises = relationship("PerformedExercise", back_populates="session")

class PerformedExercise(Base):
    __tablename__ = "performed_exercises"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    exercise_name = Column(String)
    set_number = Column(Integer)
    performed_reps = Column(Integer)
    performed_weight = Column(Float)

    session = relationship("Session", back_populates="performed_exercises")
