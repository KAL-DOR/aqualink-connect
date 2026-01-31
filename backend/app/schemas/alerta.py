from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.alerta import TipoAlerta


class AlertaBase(BaseModel):
    titulo: str
    mensaje: str
    zonas_objetivo: Optional[list[str]] = None
    tipo: TipoAlerta


class AlertaCreate(AlertaBase):
    cantidad_destinatarios: int = 0


class AlertaResponse(AlertaBase):
    id: UUID
    cantidad_destinatarios: int
    enviado_en: datetime

    class Config:
        from_attributes = True
