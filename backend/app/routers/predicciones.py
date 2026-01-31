from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.prediccion import PrediccionDemanda, PrediccionResponse
from app.services.prediccion_service import PrediccionService

router = APIRouter()


@router.post("/demanda", response_model=PrediccionResponse)
def predecir_demanda(
    datos: PrediccionDemanda,
    db: Session = Depends(get_db)
):
    """
    Predecir demanda de agua para una alcaldía específica.

    Utiliza modelos de ML para estimar la demanda basándose en:
    - Datos históricos de pedidos
    - Incidentes reportados
    - Patrones estacionales
    - Factores externos (clima, eventos, etc.)
    """
    servicio = PrediccionService(db)
    return servicio.predecir_demanda(datos.alcaldia, datos.fecha_inicio, datos.fecha_fin)


@router.get("/demanda/{alcaldia}", response_model=PrediccionResponse)
def obtener_prediccion_alcaldia(
    alcaldia: str,
    db: Session = Depends(get_db)
):
    """Obtener predicción de demanda para una alcaldía (método GET simple)"""
    servicio = PrediccionService(db)
    return servicio.predecir_demanda(alcaldia)


@router.get("/mapa-calor")
def obtener_mapa_calor(
    db: Session = Depends(get_db)
):
    """
    Obtener datos para mapa de calor de demanda en CDMX.

    Retorna predicciones para todas las alcaldías principales.
    """
    servicio = PrediccionService(db)
    alcaldias = [
        "Benito Juárez", "Coyoacán", "Cuauhtémoc", "Miguel Hidalgo",
        "Tlalpan", "Iztapalapa", "Gustavo A. Madero", "Álvaro Obregón"
    ]

    predicciones = []
    for alcaldia in alcaldias:
        pred = servicio.predecir_demanda(alcaldia)
        predicciones.append({
            "alcaldia": alcaldia,
            "demanda": pred.demanda_predicha,
            "intensidad": pred.intensidad,
            "lat": servicio.obtener_coordenadas(alcaldia)[0],
            "lng": servicio.obtener_coordenadas(alcaldia)[1]
        })

    return {"predicciones": predicciones, "timestamp": datetime.utcnow()}


@router.get("/tendencias")
def obtener_tendencias(
    dias: int = Query(7, ge=1, le=30, description="Días a analizar"),
    db: Session = Depends(get_db)
):
    """
    Obtener tendencias de demanda de los últimos N días.
    """
    servicio = PrediccionService(db)
    return servicio.analizar_tendencias(dias)
