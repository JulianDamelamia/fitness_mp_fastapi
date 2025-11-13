# app/models/user.py
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum
from app.models.associations import user_follows


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

    # --- Roles ---
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_pending_trainer = Column(Boolean, default=False, nullable=False)

    # --- Relaciones de planes ---
    created_plans = relationship('Plan', back_populates='creator')
    created_routines = relationship('Routine', back_populates='creator')
   
    purchases = relationship("Purchase", back_populates="user")
    purchased_plans = relationship(
        "Plan",
        secondary="purchases",
        viewonly=True,
        back_populates="buyers"
    )

    # --- Relaciones de observadores ---
    # Qué notificaciones tengo
    notifications = relationship(
        "Notification", 
        back_populates="user", 
        cascade="all, delete-orphan",
        order_by="desc(Notification.created_at)" # Opcional: ordenarlas
    )

    # 'following' (A quién sigo)
    following = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=(user_follows.c.follower_id == id),
        secondaryjoin=(user_follows.c.followed_id == id),
        back_populates="followed_by"
    )
    
    # 'followed_by' (mis "observers")
    followed_by = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=(user_follows.c.followed_id == id),
        secondaryjoin=(user_follows.c.follower_id == id),
        back_populates="following"
    )
