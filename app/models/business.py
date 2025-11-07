from app.db.session import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,DateTime, Float,Table, func
from sqlalchemy.orm import relationship
from app.models.associations import plans_routines
# Formato:
# class NombreSingular(Base):
#   __tablename__ = 'nombre_plural'
# atributo = Column()
# relacion = relationship('ObjetoDestino', back_populates='relacion_destino')

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    creator = relationship('User', back_populates='created_plans')
    routines =  relationship(
        'Routine',
        secondary=plans_routines,
        back_populates='plans'
    )
    purchases = relationship("Purchase", back_populates="plan")

    buyers = relationship(
        "User",
        secondary="purchases",
        viewonly=True,
        back_populates="purchased_plans"
    )

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    validation_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="purchases")
    plan = relationship("Plan", back_populates="purchases")