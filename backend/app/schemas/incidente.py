from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.incidente import TipoIncidente, EstadoIncidente


class IncidenteBase(BaseModel):
    ciudadano_id: Optional[UUID] = None
    tipo: TipoIncidente
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None
    descripcion: Optional[str] = None
    hogares_afectados: int = 1
    duracion: Optional[str] = None


class IncidenteCreate(IncidenteBase):
    pass


class IncidenteUpdate(BaseModel):
    estado: Optional[EstadoIncidente] = None
    descripcion: Optional[str] = None
    hogares_afectados: Optional[int] = None


class IncidenteResponse(IncidenteBase):
    id: UUID
    estado: EstadoIncidente
    creado_en: datetime
    reconocido_en: Optional[datetime] = None
    resuelto_en: Optional[datetime] = None
    actualizado_en: datetime

    class Config:
        from_attributes = True
