from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import quejas, alertas, predicciones, incidentes, hotspots

settings = get_settings()

app = FastAPI(
    title="AquaHub API",
    version=settings.app_version,
    description="API para recopilar quejas de agua desde redes sociales y predicciones",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a AquaHub API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"estado": "saludable"}


# Register routers
app.include_router(quejas.router, prefix="/api/quejas", tags=["Quejas de Twitter/X"])
app.include_router(alertas.router, prefix="/api/alertas", tags=["Alertas"])
app.include_router(predicciones.router, prefix="/api/predicciones", tags=["Predicciones ML"])
app.include_router(incidentes.router, prefix="/api/incidentes", tags=["Incidentes"])
app.include_router(hotspots.router, prefix="/api/hotspots", tags=["Hotspots/Risk Zones"])
