from sqlalchemy import Column, String, Numeric, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Ciudadano(Base):
    __tablename__ = "ciudadanos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(255))
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    direccion = Column(String)
    colonia = Column(String(255))
    alcaldia = Column(String(255))
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
