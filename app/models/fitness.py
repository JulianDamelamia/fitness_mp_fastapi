# app/models/fitness.py
from app.db.session import Base # Importa Base desde la nueva ubicación
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


# # Ejercicio como elemento abstracto que compone las sesiones
# class ExerciseTemplate(Base):
#     __tablename__ = "exercise_templates"
#     id = Column(Integer, primary_key=True)
#     session_template_id = Column(Integer, ForeignKey("session_templates.id"))
#     exercise_name = Column(String)
#     target_sets = Column(Integer)
#     target_reps = Column(Integer)
#     target_weight = Column(Float, nullable=True)

#     session_template = relationship("SessionTemplate", back_populates="exercises")

#     primary_muscles = Column(JSON)   # e.g., ["pecho", "tríceps"]
#     secondary_muscles = Column(JSON) # e.g., ["hombros"]

# class Purchase(Base):
#     __tablename__ = "purchases"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     plan_id = Column(Integer, ForeignKey("plans.id"))
#     purchase_date = Column(DateTime, default=datetime.now(timezone.utc))

#     sessions = relationship("Session", back_populates="purchase")

# # Sesión concreta realizada por el usuario
# class Session(Base):
#     __tablename__ = "sessions"
#     id = Column(Integer, primary_key=True)
#     purchase_id = Column(Integer, ForeignKey("purchases.id"))
#     session_template_id = Column(Integer, ForeignKey("session_templates.id"))
#     date = Column(DateTime, default=datetime.now(timezone.utc))

#     purchase = relationship("Purchase", back_populates="sessions")
#     session_template = relationship("SessionTemplate")
#     performed_exercises = relationship("PerformedExercise", back_populates="session")

# class PerformedExercise(Base):
#     __tablename__ = "performed_exercises"
#     id = Column(Integer, primary_key=True)
#     session_id = Column(Integer, ForeignKey("sessions.id"))
#     exercise_name = Column(String)
#     set_number = Column(Integer)
#     performed_reps = Column(Integer)
#     performed_weight = Column(Float)

#     session = relationship("Session", back_populates="performed_exercises")
