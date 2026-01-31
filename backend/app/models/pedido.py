from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class EstadoPedido(str, enum.Enum):
    pendiente = "pendiente"
    aceptado = "aceptado"
    en_transito = "en_transito"
    entregado = "entregado"
    cancelado = "cancelado"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores.id"))
    ciudadano_id = Column(UUID(as_uuid=True), ForeignKey("ciudadanos.id"))
    nombre_ciudadano = Column(String(255))
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    direccion = Column(String)
    colonia = Column(String(255))
    alcaldia = Column(String(255))
    cantidad_litros = Column(Integer, nullable=False)
    precio_total = Column(Numeric(10, 2), nullable=False)
    subsidio_aplicado = Column(Numeric(10, 2), default=0.00)
    estado = Column(Enum(EstadoPedido, name="estado_pedido", create_type=False), default=EstadoPedido.pendiente)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    aceptado_en = Column(TIMESTAMP)
    entregado_en = Column(TIMESTAMP)
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
