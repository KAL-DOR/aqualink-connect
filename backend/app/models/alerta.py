from sqlalchemy import Column, String, Integer, TIMESTAMP, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class TipoAlerta(str, enum.Enum):
    escasez = "escasez"
    conservacion = "conservacion"
    programa = "programa"
    emergencia = "emergencia"


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(255), nullable=False)
    mensaje = Column(String, nullable=False)
    zonas_objetivo = Column(ARRAY(String))
    cantidad_destinatarios = Column(Integer, default=0)
    tipo = Column(Enum(TipoAlerta, name="tipo_alerta", create_type=False), nullable=False)
    enviado_en = Column(TIMESTAMP, server_default=func.now())
