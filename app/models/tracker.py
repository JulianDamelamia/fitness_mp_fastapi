from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float,String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now(timezone.utc))

    #relación con la sesión abstracta
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates='session_logs')
    
    # Relación con el usuario que realizó el log
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="session_logs")

    #relación con los ejercicios logueados
    exercise_logs = relationship("ExerciseLog", back_populates="session_logs", cascade="all, delete-orphan")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"
    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    set_n = Column(Integer, nullable=False)

    session_log_id = Column(Integer, ForeignKey("session_logs.id"), nullable=False)
    session_logs = relationship("SessionLog", back_populates="exercise_logs")

    
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    exercise = relationship("Exercise", back_populates="logs", lazy="joined")
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
