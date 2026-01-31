from sqlalchemy import Column, String, Numeric, Integer, Boolean, ARRAY, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    calificacion = Column(Numeric(2, 1), default=0.0)
    precio_por_litro = Column(Numeric(10, 2), nullable=False)
    tiempo_estimado_llegada = Column(String(50))
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    direccion = Column(String)
    colonia = Column(String(255))
    alcaldia = Column(String(255))
    tamano_flota = Column(Integer, default=1)
    disponible = Column(Boolean, default=True)
    certificaciones = Column(ARRAY(String))
    telefono = Column(String(20))
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
