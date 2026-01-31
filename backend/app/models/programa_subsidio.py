from sqlalchemy import Column, String, Numeric, Integer, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class ProgramaSubsidio(Base):
    __tablename__ = "programas_subsidio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    presupuesto = Column(Numeric(12, 2), nullable=False)
    gastado = Column(Numeric(12, 2), default=0.00)
    beneficiarios = Column(Integer, default=0)
    porcentaje_descuento = Column(Integer, nullable=False)
    criterios_elegibilidad = Column(String)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
