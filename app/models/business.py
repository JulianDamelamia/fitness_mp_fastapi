from app.db.session import Base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, Text, Float,DateTime, Table
from datetime import datetime, timezone
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