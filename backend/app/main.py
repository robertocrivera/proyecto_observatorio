from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import settings, BASE_DIR
from app.db.session import SessionLocal
from app.db.seeder import init_db
from app.controllers.demografia_controller import router as demografia_router
from app.controllers.leads_controller import router as leads_router
from app.controllers.geo_controller import router as geo_router
from app.controllers.estrategia_controller import router as estrategia_router
from app.controllers.suscripcion_controller import router as suscripcion_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API RESTful de Inteligencia Demográfica, Web GIS y Gestión Estratégica Educativa para Colombia."
)

# 1. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Inicialización de la base de datos y datos semilla en el arranque
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

# 3. Registro de Controladores REST
app.include_router(demografia_router, prefix=settings.API_V1_STR)
app.include_router(leads_router, prefix=settings.API_V1_STR)
app.include_router(geo_router, prefix=settings.API_V1_STR)
app.include_router(estrategia_router, prefix=settings.API_V1_STR)
app.include_router(suscripcion_router, prefix=settings.API_V1_STR)

# 4. Servir Frontend Estático y Assets
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    css_dir = frontend_dir / "css"
    js_dir = frontend_dir / "js"
    assets_dir = frontend_dir / "assets"
    
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
def read_root():
    index_path = BASE_DIR / "frontend" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Bienvenido a Edudemia API. Acceda a /docs para la documentación interactiva."}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
