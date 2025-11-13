#para resolver importaciones circulares
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.session import Base

routines_sessions = Table(
    "routines_sessions",
    Base.metadata,
    Column("routine_id", ForeignKey("routines.id"), primary_key=True),
    Column("session_id", ForeignKey("sessions.id"), primary_key=True)
)
plans_routines = Table(
    "plans_routines",
    Base.metadata,
    Column("plan_id", ForeignKey("plans.id"), primary_key=True),
    Column("routine_id", ForeignKey("routines.id"), primary_key=True)
)

user_follows = Table(
    "user_follows",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True),
    Column("followed_id", ForeignKey("users.id"), primary_key=True)
)