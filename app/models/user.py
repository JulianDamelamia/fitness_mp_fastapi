import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import event

from app.db.session import Base
from app.models.associations import user_follows
from app.interfaces.observer import Subject, Observer


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
    created_plans = relationship("Plan", back_populates="creator")
    created_routines = relationship("Routine", back_populates="creator")

    created_sessions = relationship("Session", back_populates="creator")

    purchases = relationship("Purchase", back_populates="user")
    purchased_plans = relationship(
        "Plan", secondary="purchases", viewonly=True, back_populates="buyers"
    )

    # --- Relaciones de observadores ---
    # Qué notificaciones tengo
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Notification.created_at)",
    )

    # 'following' (A quién sigo)
    following = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=(user_follows.c.follower_id == id),
        secondaryjoin=(user_follows.c.followed_id == id),
        back_populates="followed_by",
    )

    # 'followed_by' (mis "observers")
    followed_by = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=(user_follows.c.followed_id == id),
        secondaryjoin=(user_follows.c.follower_id == id),
        back_populates="following",
    )

    # Relación con los entrenamientos que este usuario registró
    session_logs = relationship(
        "SessionLog",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(SessionLog.date)",
    )

    def registerObserver(self, observer: Observer) -> None:
        if hasattr(self, "subject_delegate"):
            self.subject_delegate.registerObserver(observer)

    def removeObserver(self, observer: Observer) -> None:
        if hasattr(self, "subject_delegate"):
            self.subject_delegate.removeObserver(observer)

    def notifyObservers(self, event_data: any) -> None:
        if hasattr(self, "subject_delegate"):
            self.subject_delegate.notifyObservers(event_data)


@event.listens_for(User, "load")
@event.listens_for(User, "init")
def init_subject(target, *args, **kwargs):
    """
    Crea una instancia de Subject dentro del objeto User,
    pasando el propio User (target) como el delegator.
    """
    target.subject_delegate = Subject(delegator=target)
