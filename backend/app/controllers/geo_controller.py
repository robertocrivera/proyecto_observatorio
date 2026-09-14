from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.geo_service import GeoService
from app.schemas.schemas import GeoRadioResponseOut

router = APIRouter(prefix="/geo", tags=["Geolocalización & Radio 5km"])

@router.get("/colegios-redonda", response_model=GeoRadioResponseOut)
def get_colegios_en_radio(
    lat: float = Query(4.6732, description="Latitud de origen (por defecto Fontibón, Bogotá)"),
    lng: float = Query(-74.1448, description="Longitud de origen"),
    radio_km: float = Query(5.0, ge=0.5, le=50.0, description="Radio de búsqueda en kilómetros"),
    municipio_id: Optional[int] = Query(1, description="ID de referencia del municipio"),
    db: Session = Depends(get_db)
):
    """
    Módulo C.1: Búsqueda activa en radio dinámico (5 km por defecto).
    Aplica la fórmula de Haversine para filtrar colegios oficiales, privados y demanda activa.
    """
    service = GeoService(db)
    return service.get_colegios_y_demanda_en_radio(lat, lng, radio_km, municipio_id)

