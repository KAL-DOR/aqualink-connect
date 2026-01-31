from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class TipoIncidente(str, enum.Enum):
    fuga = "fuga"
    sin_agua = "sin_agua"
    contaminacion = "contaminacion"
    infraestructura = "infraestructura"
    otro = "otro"


class EstadoIncidente(str, enum.Enum):
    pendiente = "pendiente"
    reconocido = "reconocido"
    en_progreso = "en_progreso"
    resuelto = "resuelto"


class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ciudadano_id = Column(UUID(as_uuid=True), ForeignKey("ciudadanos.id"))
    tipo = Column(Enum(TipoIncidente, name="tipo_incidente", create_type=False), nullable=False)
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    direccion = Column(String)
    colonia = Column(String(255))
    alcaldia = Column(String(255))
    descripcion = Column(String)
    hogares_afectados = Column(Integer, default=1)
    duracion = Column(String(100))
    estado = Column(Enum(EstadoIncidente, name="estado_incidente", create_type=False), default=EstadoIncidente.pendiente)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    reconocido_en = Column(TIMESTAMP)
    resuelto_en = Column(TIMESTAMP)
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
