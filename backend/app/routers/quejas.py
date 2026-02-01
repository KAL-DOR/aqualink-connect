from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.queja import Queja, TipoQueja

router = APIRouter()


# Response models
class QuejaPunto(BaseModel):
    id: int
    lat: float
    lng: float
    tipo: str
    texto: str
    username: Optional[str] = None
    alcaldia: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuejasMapResponse(BaseModel):
    puntos: List[QuejaPunto]
    total: int
    con_ubicacion: int


class QuejaDetalle(BaseModel):
    id: int
    tweet_id: str
    texto: str
    tipo: str
    username: str
    user_name: str
    likes: int
    retweets: int
    replies: int
    views: int
    latitud: Optional[float]
    longitud: Optional[float]
    alcaldia: Optional[str]
    colonia: Optional[str]
    tweet_url: str
    tweet_created_at: datetime

    class Config:
        from_attributes = True


class EstadisticasResponse(BaseModel):
    total: int
    con_ubicacion: int
    por_tipo: dict


class QuejaCreate(BaseModel):
    lat: float
    lng: float
    tipo: str
    texto: str
    username: Optional[str] = "usuario_anonimo"
    alcaldia: Optional[str] = None
    por_alcaldia: dict
    ultimas_24h: int


@router.get("/mapa", response_model=QuejasMapResponse)
async def get_quejas_mapa(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: sin_agua, fuga, agua_contaminada, baja_presion"),
    alcaldia: Optional[str] = Query(None, description="Filtrar por alcaldía"),
    limit: int = Query(1000, ge=1, le=5000, description="Máximo de puntos a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtener quejas para mostrar en el mapa.
    Solo retorna quejas que tienen ubicación (lat/lng).
    """
    query = db.query(Queja).filter(Queja.latitud.isnot(None))

    if tipo:
        try:
            tipo_enum = TipoQueja(tipo.lower())
            query = query.filter(Queja.tipo == tipo_enum)
        except ValueError:
            pass

    if alcaldia:
        query = query.filter(Queja.alcaldia.ilike(f"%{alcaldia}%"))

    # Order by most recent
    query = query.order_by(Queja.tweet_created_at.desc())

    quejas = query.limit(limit).all()

    puntos = [
        QuejaPunto(
            id=q.id,
            lat=q.latitud,
            lng=q.longitud,
            tipo=q.tipo.value if q.tipo else "otro",
            texto=q.texto[:200] + "..." if len(q.texto) > 200 else q.texto,
            username=q.username or "anonymous",
            alcaldia=q.alcaldia,
            created_at=q.tweet_created_at or q.created_at
        )
        for q in quejas
    ]

    total = db.query(Queja).count()
    con_ubicacion = db.query(Queja).filter(Queja.latitud.isnot(None)).count()

    return QuejasMapResponse(
        puntos=puntos,
        total=total,
        con_ubicacion=con_ubicacion
    )


@router.get("/estadisticas", response_model=EstadisticasResponse)
async def get_estadisticas(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de las quejas.
    """
    total = db.query(Queja).count()
    con_ubicacion = db.query(Queja).filter(Queja.latitud.isnot(None)).count()

    # Por tipo
    por_tipo_raw = db.query(Queja.tipo, func.count(Queja.id)).group_by(Queja.tipo).all()
    por_tipo = {t.value if t else "otro": c for t, c in por_tipo_raw}

    # Por alcaldía
    por_alcaldia_raw = (
        db.query(Queja.alcaldia, func.count(Queja.id))
        .filter(Queja.alcaldia.isnot(None))
        .group_by(Queja.alcaldia)
        .order_by(func.count(Queja.id).desc())
        .limit(15)
        .all()
    )
    por_alcaldia = {a: c for a, c in por_alcaldia_raw}

    # Últimas 24h
    from datetime import timedelta
    hace_24h = datetime.utcnow() - timedelta(hours=24)
    ultimas_24h = db.query(Queja).filter(Queja.tweet_created_at >= hace_24h).count()

    return EstadisticasResponse(
        total=total,
        con_ubicacion=con_ubicacion,
        por_tipo=por_tipo,
        por_alcaldia=por_alcaldia,
        ultimas_24h=ultimas_24h
    )


@router.post("", response_model=QuejaPunto)
async def create_queja(queja: QuejaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva queja desde el frontend.
    """
    import uuid

    # Map tipo string to enum
    try:
        tipo_enum = TipoQueja(queja.tipo.lower())
    except ValueError:
        tipo_enum = TipoQueja.OTRO

    nueva_queja = Queja(
        tweet_id=f"user_{uuid.uuid4().hex[:12]}",
        texto=queja.texto,
        tipo=tipo_enum,
        username=queja.username or "usuario_anonimo",
        latitud=queja.lat,
        longitud=queja.lng,
        alcaldia=queja.alcaldia,
        tweet_created_at=datetime.utcnow(),
    )

    db.add(nueva_queja)
    db.commit()
    db.refresh(nueva_queja)

    return QuejaPunto(
        id=nueva_queja.id,
        lat=nueva_queja.latitud,
        lng=nueva_queja.longitud,
        tipo=nueva_queja.tipo.value if nueva_queja.tipo else "otro",
        texto=nueva_queja.texto,
        username=nueva_queja.username,
        alcaldia=nueva_queja.alcaldia,
        created_at=nueva_queja.tweet_created_at or nueva_queja.created_at
    )


@router.get("/lista", response_model=List[QuejaDetalle])
async def get_quejas_lista(
    tipo: Optional[str] = Query(None),
    alcaldia: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de quejas con detalles completos.
    """
    query = db.query(Queja)

    if tipo:
        try:
            tipo_enum = TipoQueja(tipo.lower())
            query = query.filter(Queja.tipo == tipo_enum)
        except ValueError:
            pass

    if alcaldia:
        query = query.filter(Queja.alcaldia.ilike(f"%{alcaldia}%"))

    quejas = (
        query
        .order_by(Queja.tweet_created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        QuejaDetalle(
            id=q.id,
            tweet_id=q.tweet_id,
            texto=q.texto,
            tipo=q.tipo.value if q.tipo else "otro",
            username=q.username,
            user_name=q.user_name or "",
            likes=q.likes or 0,
            retweets=q.retweets or 0,
            replies=q.replies or 0,
            views=q.views or 0,
            latitud=q.latitud,
            longitud=q.longitud,
            alcaldia=q.alcaldia,
            colonia=q.colonia,
            tweet_url=q.tweet_url or "",
            tweet_created_at=q.tweet_created_at
        )
        for q in quejas
    ]


@router.get("/{queja_id}", response_model=QuejaDetalle)
async def get_queja(queja_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalle de una queja específica.
    """
    queja = db.query(Queja).filter(Queja.id == queja_id).first()
    if not queja:
        raise HTTPException(status_code=404, detail="Queja no encontrada")

    return QuejaDetalle(
        id=queja.id,
        tweet_id=queja.tweet_id,
        texto=queja.texto,
        tipo=queja.tipo.value if queja.tipo else "otro",
        username=queja.username,
        user_name=queja.user_name or "",
        likes=queja.likes or 0,
        retweets=queja.retweets or 0,
        replies=queja.replies or 0,
        views=queja.views or 0,
        latitud=queja.latitud,
        longitud=queja.longitud,
        alcaldia=queja.alcaldia,
        colonia=queja.colonia,
        tweet_url=queja.tweet_url or "",
        tweet_created_at=queja.tweet_created_at
    )
