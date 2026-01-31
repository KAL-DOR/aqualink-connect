from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.pedido import Pedido, EstadoPedido
from app.schemas.pedido import PedidoCreate, PedidoUpdate, PedidoResponse

router = APIRouter()


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    estado: Optional[EstadoPedido] = Query(None, description="Filtrar por estado"),
    proveedor_id: Optional[UUID] = Query(None, description="Filtrar por proveedor"),
    alcaldia: Optional[str] = Query(None, description="Filtrar por alcaldía"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de pedidos de agua"""
    query = db.query(Pedido)

    if estado:
        query = query.filter(Pedido.estado == estado)
    if proveedor_id:
        query = query.filter(Pedido.proveedor_id == proveedor_id)
    if alcaldia:
        query = query.filter(Pedido.alcaldia.ilike(f"%{alcaldia}%"))

    return query.order_by(Pedido.creado_en.desc()).offset(skip).limit(limit).all()


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Obtener un pedido por ID"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.post("/", response_model=PedidoResponse, status_code=201)
def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo pedido de agua"""
    db_pedido = Pedido(**pedido.model_dump())
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.patch("/{pedido_id}", response_model=PedidoResponse)
def actualizar_pedido(
    pedido_id: UUID,
    pedido: PedidoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar estado de un pedido"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    update_data = pedido.model_dump(exclude_unset=True)

    # Actualizar timestamps según el estado
    if "estado" in update_data:
        nuevo_estado = update_data["estado"]
        if nuevo_estado == EstadoPedido.aceptado and not db_pedido.aceptado_en:
            db_pedido.aceptado_en = datetime.utcnow()
        elif nuevo_estado == EstadoPedido.entregado and not db_pedido.entregado_en:
            db_pedido.entregado_en = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_pedido, key, value)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.post("/{pedido_id}/aceptar", response_model=PedidoResponse)
def aceptar_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Aceptar un pedido pendiente"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if db_pedido.estado != EstadoPedido.pendiente:
        raise HTTPException(status_code=400, detail="Solo se pueden aceptar pedidos pendientes")

    db_pedido.estado = EstadoPedido.aceptado
    db_pedido.aceptado_en = datetime.utcnow()
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.post("/{pedido_id}/entregar", response_model=PedidoResponse)
def entregar_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Marcar un pedido como entregado"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if db_pedido.estado not in [EstadoPedido.aceptado, EstadoPedido.en_transito]:
        raise HTTPException(status_code=400, detail="El pedido debe estar aceptado o en tránsito")

    db_pedido.estado = EstadoPedido.entregado
    db_pedido.entregado_en = datetime.utcnow()
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


@router.post("/{pedido_id}/cancelar", response_model=PedidoResponse)
def cancelar_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Cancelar un pedido"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if db_pedido.estado == EstadoPedido.entregado:
        raise HTTPException(status_code=400, detail="No se puede cancelar un pedido entregado")

    db_pedido.estado = EstadoPedido.cancelado
    db.commit()
    db.refresh(db_pedido)
    return db_pedido
