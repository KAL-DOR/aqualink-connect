from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import proveedores, pedidos, incidentes, alertas, predicciones

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para coordinación de servicios de agua durante escasez",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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


# Registrar routers
app.include_router(proveedores.router, prefix="/api/proveedores", tags=["Proveedores"])
app.include_router(pedidos.router, prefix="/api/pedidos", tags=["Pedidos"])
app.include_router(incidentes.router, prefix="/api/incidentes", tags=["Incidentes"])
app.include_router(alertas.router, prefix="/api/alertas", tags=["Alertas"])
app.include_router(predicciones.router, prefix="/api/predicciones", tags=["Predicciones ML"])
