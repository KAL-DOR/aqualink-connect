from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.incidente import Incidente, TipoIncidente, EstadoIncidente
from app.schemas.incidente import IncidenteCreate, IncidenteUpdate, IncidenteResponse

router = APIRouter()


@router.get("/", response_model=list[IncidenteResponse])
def listar_incidentes(
    tipo: Optional[TipoIncidente] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoIncidente] = Query(None, description="Filtrar por estado"),
    alcaldia: Optional[str] = Query(None, description="Filtrar por alcaldía"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de incidentes reportados"""
    query = db.query(Incidente)

    if tipo:
        query = query.filter(Incidente.tipo == tipo)
    if estado:
        query = query.filter(Incidente.estado == estado)
    if alcaldia:
        query = query.filter(Incidente.alcaldia.ilike(f"%{alcaldia}%"))

    return query.order_by(Incidente.creado_en.desc()).offset(skip).limit(limit).all()


@router.get("/estadisticas")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de incidentes"""
    total = db.query(Incidente).count()
    pendientes = db.query(Incidente).filter(Incidente.estado == EstadoIncidente.pendiente).count()
    en_progreso = db.query(Incidente).filter(Incidente.estado == EstadoIncidente.en_progreso).count()
    resueltos = db.query(Incidente).filter(Incidente.estado == EstadoIncidente.resuelto).count()

    por_tipo = {}
    for tipo in TipoIncidente:
        por_tipo[tipo.value] = db.query(Incidente).filter(Incidente.tipo == tipo).count()

    return {
        "total": total,
        "pendientes": pendientes,
        "en_progreso": en_progreso,
        "resueltos": resueltos,
        "por_tipo": por_tipo
    }


@router.get("/{incidente_id}", response_model=IncidenteResponse)
def obtener_incidente(incidente_id: UUID, db: Session = Depends(get_db)):
    """Obtener un incidente por ID"""
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente


@router.post("/", response_model=IncidenteResponse, status_code=201)
def crear_incidente(incidente: IncidenteCreate, db: Session = Depends(get_db)):
    """Reportar un nuevo incidente"""
    db_incidente = Incidente(**incidente.model_dump())
    db.add(db_incidente)
    db.commit()
    db.refresh(db_incidente)
    return db_incidente


@router.patch("/{incidente_id}", response_model=IncidenteResponse)
def actualizar_incidente(
    incidente_id: UUID,
    incidente: IncidenteUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un incidente"""
    db_incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not db_incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    update_data = incidente.model_dump(exclude_unset=True)

    # Actualizar timestamps según el estado
    if "estado" in update_data:
        nuevo_estado = update_data["estado"]
        if nuevo_estado == EstadoIncidente.reconocido and not db_incidente.reconocido_en:
            db_incidente.reconocido_en = datetime.utcnow()
        elif nuevo_estado == EstadoIncidente.resuelto and not db_incidente.resuelto_en:
            db_incidente.resuelto_en = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_incidente, key, value)

    db.commit()
    db.refresh(db_incidente)
    return db_incidente


@router.post("/{incidente_id}/reconocer", response_model=IncidenteResponse)
def reconocer_incidente(incidente_id: UUID, db: Session = Depends(get_db)):
    """Reconocer un incidente pendiente"""
    db_incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not db_incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    if db_incidente.estado != EstadoIncidente.pendiente:
        raise HTTPException(status_code=400, detail="Solo se pueden reconocer incidentes pendientes")

    db_incidente.estado = EstadoIncidente.reconocido
    db_incidente.reconocido_en = datetime.utcnow()
    db.commit()
    db.refresh(db_incidente)
    return db_incidente


@router.post("/{incidente_id}/resolver", response_model=IncidenteResponse)
def resolver_incidente(incidente_id: UUID, db: Session = Depends(get_db)):
    """Marcar un incidente como resuelto"""
    db_incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not db_incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    if db_incidente.estado == EstadoIncidente.resuelto:
        raise HTTPException(status_code=400, detail="El incidente ya está resuelto")

    db_incidente.estado = EstadoIncidente.resuelto
    db_incidente.resuelto_en = datetime.utcnow()
    db.commit()
    db.refresh(db_incidente)
    return db_incidente
