from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse

router = APIRouter()


@router.get("/", response_model=list[ProveedorResponse])
def listar_proveedores(
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    alcaldia: Optional[str] = Query(None, description="Filtrar por alcaldía"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de proveedores de agua (pipas)"""
    query = db.query(Proveedor)

    if disponible is not None:
        query = query.filter(Proveedor.disponible == disponible)
    if alcaldia:
        query = query.filter(Proveedor.alcaldia.ilike(f"%{alcaldia}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def obtener_proveedor(proveedor_id: UUID, db: Session = Depends(get_db)):
    """Obtener un proveedor por ID"""
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.post("/", response_model=ProveedorResponse, status_code=201)
def crear_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo proveedor"""
    db_proveedor = Proveedor(**proveedor.model_dump())
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor


@router.patch("/{proveedor_id}", response_model=ProveedorResponse)
def actualizar_proveedor(
    proveedor_id: UUID,
    proveedor: ProveedorUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de un proveedor"""
    db_proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    update_data = proveedor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_proveedor, key, value)

    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor


@router.delete("/{proveedor_id}", status_code=204)
def eliminar_proveedor(proveedor_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un proveedor"""
    db_proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db.delete(db_proveedor)
    db.commit()
