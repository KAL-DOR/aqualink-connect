from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ProveedorBase(BaseModel):
    nombre: str
    precio_por_litro: Decimal
    tiempo_estimado_llegada: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None
    tamano_flota: int = 1
    disponible: bool = True
    certificaciones: Optional[list[str]] = None
    telefono: Optional[str] = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    calificacion: Optional[Decimal] = None
    precio_por_litro: Optional[Decimal] = None
    tiempo_estimado_llegada: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None
    tamano_flota: Optional[int] = None
    disponible: Optional[bool] = None
    certificaciones: Optional[list[str]] = None
    telefono: Optional[str] = None


class ProveedorResponse(ProveedorBase):
    id: UUID
    calificacion: Decimal = Decimal("0.0")
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
