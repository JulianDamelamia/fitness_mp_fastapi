"""Módulo que define los modelos de Plan y Purchase para la aplicación de fitness."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.associations import plans_routines

# Formato:
# class NombreSingular(Base):
#   __tablename__ = 'nombre_plural'
# atributo = Column()
# relacion = relationship('ObjetoDestino', back_populates='relacion_destino')


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="created_plans")
    routines = relationship("Routine", secondary=plans_routines, back_populates="plans")
    purchases = relationship(
        "Purchase", back_populates="plan", cascade="all, delete-orphan"
    )

    buyers = relationship(
        "User", secondary="purchases", viewonly=True, back_populates="purchased_plans"
    )


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    purchase_date = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="purchases")
    plan = relationship("Plan", back_populates="purchases")
