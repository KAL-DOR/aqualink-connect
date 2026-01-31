from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.pedido import EstadoPedido


class PedidoBase(BaseModel):
    proveedor_id: UUID
    ciudadano_id: Optional[UUID] = None
    nombre_ciudadano: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    alcaldia: Optional[str] = None
    cantidad_litros: int
    precio_total: Decimal
    subsidio_aplicado: Decimal = Decimal("0.00")


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    estado: Optional[EstadoPedido] = None
    subsidio_aplicado: Optional[Decimal] = None


class PedidoResponse(PedidoBase):
    id: UUID
    estado: EstadoPedido
    creado_en: datetime
    aceptado_en: Optional[datetime] = None
    entregado_en: Optional[datetime] = None
    actualizado_en: datetime

    class Config:
        from_attributes = True
