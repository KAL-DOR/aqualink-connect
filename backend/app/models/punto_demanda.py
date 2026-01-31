from sqlalchemy import Column, String, Numeric, Integer, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class IntensidadDemanda(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class PuntoDemanda(Base):
    __tablename__ = "puntos_demanda"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    direccion = Column(String)
    colonia = Column(String(255))
    alcaldia = Column(String(255))
    intensidad = Column(Enum(IntensidadDemanda, name="intensidad_demanda", create_type=False), default=IntensidadDemanda.baja)
    cantidad_solicitudes = Column(Integer, default=0)
    registrado_en = Column(TIMESTAMP, server_default=func.now())
