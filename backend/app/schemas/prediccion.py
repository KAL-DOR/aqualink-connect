from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PrediccionDemanda(BaseModel):
    alcaldia: str
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None


class PrediccionResponse(BaseModel):
    alcaldia: str
    demanda_predicha: float
    intensidad: str
    confianza: float
    factores: dict
    recomendaciones: list[str]
    timestamp: datetime
