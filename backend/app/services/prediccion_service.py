from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import random

from app.models.pedido import Pedido
from app.models.incidente import Incidente
from app.schemas.prediccion import PrediccionResponse


class PrediccionService:
    """
    Servicio de predicción de demanda de agua.

    TODO: Integrar modelos de ML reales (scikit-learn, TensorFlow, etc.)
    Por ahora usa datos simulados para demostración.
    """

    # Coordenadas aproximadas de alcaldías de CDMX
    COORDENADAS_ALCALDIAS = {
        "Benito Juárez": (19.3984, -99.1711),
        "Coyoacán": (19.3467, -99.1617),
        "Cuauhtémoc": (19.4326, -99.1332),
        "Miguel Hidalgo": (19.4342, -99.2036),
        "Tlalpan": (19.2925, -99.1700),
        "Iztapalapa": (19.3553, -99.0628),
        "Gustavo A. Madero": (19.4819, -99.1169),
        "Álvaro Obregón": (19.3590, -99.2630),
        "Azcapotzalco": (19.4869, -99.1836),
        "Venustiano Carranza": (19.4242, -99.1058),
    }

    # Factores base de demanda por alcaldía (simulados)
    FACTORES_BASE = {
        "Benito Juárez": 0.7,
        "Coyoacán": 0.8,
        "Cuauhtémoc": 0.6,
        "Miguel Hidalgo": 0.5,
        "Tlalpan": 0.9,
        "Iztapalapa": 1.0,
        "Gustavo A. Madero": 0.85,
        "Álvaro Obregón": 0.75,
        "Azcapotzalco": 0.65,
        "Venustiano Carranza": 0.7,
    }

    def __init__(self, db: Session):
        self.db = db

    def predecir_demanda(
        self,
        alcaldia: str,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None
    ) -> PrediccionResponse:
        """
        Predecir demanda de agua para una alcaldía.

        En producción, esto usaría modelos de ML entrenados con:
        - Datos históricos de pedidos
        - Reportes de incidentes
        - Datos climáticos
        - Eventos especiales
        - Patrones estacionales
        """
        # Obtener factor base de la alcaldía
        factor_base = self.FACTORES_BASE.get(alcaldia, 0.7)

        # Contar pedidos recientes (últimos 7 días)
        hace_7_dias = datetime.utcnow() - timedelta(days=7)
        pedidos_recientes = self.db.query(Pedido).filter(
            Pedido.alcaldia.ilike(f"%{alcaldia}%"),
            Pedido.creado_en >= hace_7_dias
        ).count()

        # Contar incidentes activos
        incidentes_activos = self.db.query(Incidente).filter(
            Incidente.alcaldia.ilike(f"%{alcaldia}%"),
            Incidente.estado.in_(["pendiente", "reconocido", "en_progreso"])
        ).count()

        # Calcular demanda predicha (simulación)
        # En producción, aquí se invocaría el modelo de ML
        demanda_base = 100 * factor_base
        ajuste_pedidos = pedidos_recientes * 2
        ajuste_incidentes = incidentes_activos * 15
        variacion = random.uniform(-10, 10)

        demanda_predicha = demanda_base + ajuste_pedidos + ajuste_incidentes + variacion
        demanda_predicha = max(0, min(demanda_predicha, 200))  # Normalizar entre 0-200

        # Determinar intensidad
        if demanda_predicha < 50:
            intensidad = "baja"
        elif demanda_predicha < 100:
            intensidad = "media"
        elif demanda_predicha < 150:
            intensidad = "alta"
        else:
            intensidad = "critica"

        # Calcular confianza (simulada)
        confianza = 0.75 + random.uniform(0, 0.2)

        # Generar factores explicativos
        factores = {
            "factor_base_zona": factor_base,
            "pedidos_recientes": pedidos_recientes,
            "incidentes_activos": incidentes_activos,
            "temporada": self._obtener_temporada(),
            "dia_semana": datetime.utcnow().strftime("%A"),
        }

        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(intensidad, incidentes_activos)

        return PrediccionResponse(
            alcaldia=alcaldia,
            demanda_predicha=round(demanda_predicha, 2),
            intensidad=intensidad,
            confianza=round(confianza, 2),
            factores=factores,
            recomendaciones=recomendaciones,
            timestamp=datetime.utcnow()
        )

    def obtener_coordenadas(self, alcaldia: str) -> tuple[float, float]:
        """Obtener coordenadas de una alcaldía"""
        return self.COORDENADAS_ALCALDIAS.get(alcaldia, (19.4326, -99.1332))

    def analizar_tendencias(self, dias: int) -> dict:
        """Analizar tendencias de demanda de los últimos N días"""
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)

        # Contar pedidos por día (simulación)
        tendencia = []
        for i in range(dias):
            fecha = fecha_inicio + timedelta(days=i)
            pedidos = self.db.query(Pedido).filter(
                Pedido.creado_en >= fecha,
                Pedido.creado_en < fecha + timedelta(days=1)
            ).count()
            tendencia.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "pedidos": pedidos,
                "demanda_estimada": pedidos * 1000  # Litros estimados
            })

        # Calcular métricas
        total_pedidos = sum(t["pedidos"] for t in tendencia)
        promedio_diario = total_pedidos / dias if dias > 0 else 0

        return {
            "periodo_dias": dias,
            "total_pedidos": total_pedidos,
            "promedio_diario": round(promedio_diario, 2),
            "tendencia": tendencia,
            "timestamp": datetime.utcnow()
        }

    def _obtener_temporada(self) -> str:
        """Obtener temporada actual"""
        mes = datetime.utcnow().month
        if mes in [12, 1, 2]:
            return "invierno"
        elif mes in [3, 4, 5]:
            return "primavera"
        elif mes in [6, 7, 8]:
            return "verano"
        else:
            return "otoño"

    def _generar_recomendaciones(self, intensidad: str, incidentes: int) -> list[str]:
        """Generar recomendaciones basadas en la predicción"""
        recomendaciones = []

        if intensidad == "critica":
            recomendaciones.append("Activar protocolo de emergencia hídrica")
            recomendaciones.append("Coordinar con proveedores adicionales")
            recomendaciones.append("Emitir alerta pública de conservación")
        elif intensidad == "alta":
            recomendaciones.append("Aumentar capacidad de distribución")
            recomendaciones.append("Monitorear inventario de proveedores")
        elif intensidad == "media":
            recomendaciones.append("Mantener operación normal con monitoreo")

        if incidentes > 3:
            recomendaciones.append(f"Priorizar resolución de {incidentes} incidentes activos")

        if not recomendaciones:
            recomendaciones.append("Situación estable, continuar operación normal")

        return recomendaciones
