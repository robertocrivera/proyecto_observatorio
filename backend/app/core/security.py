import html
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from jose import jwt, JWTError
import bcrypt
from app.core.config import settings

class InputSanitizer:
    """Sanitización de entradas para mitigar XSS y ataques de inyección."""
    
    @staticmethod
    def sanitize_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return text
        # Eliminar etiquetas html peligrosas o scripts
        clean_text = html.escape(text.strip())
        # Remover caracteres de control nulos
        clean_text = clean_text.replace("\0", "")
        return clean_text
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        regex = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,8}$"
        return bool(re.match(regex, email))

class SecurityManager:
    """Manejo de tokens JWT, hashing seguro y generación de tokens de sesión."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    @staticmethod
    def generate_session_token(lead_email: str) -> str:
        """Genera un token de sesión criptográfico para desbloqueo de descargas y upsell."""
        prefix = secrets.token_hex(8)
        now_ts = int(time.time())
        raw = f"EDU-{prefix}-{now_ts}"
        return raw

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

class InMemoryRateLimiter:
    """Control de tasa de peticiones (Rate Limiting) en memoria por IP."""
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_log: Dict[str, List[float]] = {}
        
    def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        timestamps = self.requests_log.get(client_ip, [])
        # Filtrar marcas de tiempo dentro de la ventana actual
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        
        if len(valid_timestamps) >= self.max_requests:
            self.requests_log[client_ip] = valid_timestamps
            return True
        
        valid_timestamps.append(now)
        self.requests_log[client_ip] = valid_timestamps
        return False

# Instancias globales
rate_limiter = InMemoryRateLimiter(
    max_requests=settings.RATE_LIMIT_REQUESTS, 
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS
)

