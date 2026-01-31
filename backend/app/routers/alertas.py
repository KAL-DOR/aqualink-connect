from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.alerta import Alerta, TipoAlerta
from app.schemas.alerta import AlertaCreate, AlertaResponse

router = APIRouter()


@router.get("/", response_model=list[AlertaResponse])
def listar_alertas(
    tipo: Optional[TipoAlerta] = Query(None, description="Filtrar por tipo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de alertas enviadas"""
    query = db.query(Alerta)

    if tipo:
        query = query.filter(Alerta.tipo == tipo)

    return query.order_by(Alerta.enviado_en.desc()).offset(skip).limit(limit).all()


@router.get("/{alerta_id}", response_model=AlertaResponse)
def obtener_alerta(alerta_id: UUID, db: Session = Depends(get_db)):
    """Obtener una alerta por ID"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alerta


@router.post("/", response_model=AlertaResponse, status_code=201)
def crear_alerta(alerta: AlertaCreate, db: Session = Depends(get_db)):
    """Enviar una nueva alerta a los ciudadanos"""
    db_alerta = Alerta(**alerta.model_dump())
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)
    return db_alerta


@router.delete("/{alerta_id}", status_code=204)
def eliminar_alerta(alerta_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una alerta del historial"""
    db_alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not db_alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    db.delete(db_alerta)
    db.commit()
