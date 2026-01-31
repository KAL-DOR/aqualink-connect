from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class CiudadanoBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None


class CiudadanoCreate(CiudadanoBase):
    pass


class CiudadanoUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None


class CiudadanoResponse(CiudadanoBase):
    id: UUID
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
