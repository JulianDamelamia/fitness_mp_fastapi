# app/models/user.py
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    TRAINER = "TRAINER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_pending_trainer = Column(Boolean, default=False, nullable=False)

    created_plans = relationship('Plan', back_populates='creator')
    created_routines = relationship('Routine', back_populates='creator')
   
    purchases = relationship("Purchase", back_populates="user")
    purchased_plans = relationship(
        "Plan",
        secondary="purchases",
        viewonly=True,
        back_populates="buyers"
    )