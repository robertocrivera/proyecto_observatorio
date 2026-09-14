import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "edudemia.db"

class Settings:
    PROJECT_NAME: str = "Edudemia - Observatorio Demográfico Educativo Colombia"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de Datos SQLite (fácilmente conmutable a PostgreSQL vía DATABASE_URL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    
    # Seguridad y Tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "edudemia-secret-jwt-key-2026-colombia-secure-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 horas
    
    # Rate Limiting (Peticiones permitidas por ventana de tiempo en segundos)
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
settings = Settings()

