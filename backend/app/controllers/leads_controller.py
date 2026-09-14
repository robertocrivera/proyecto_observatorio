from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
import json
from app.db.session import get_db
from app.services.leads_service import LeadsService
from app.services.demografia_service import DemografiaService
from app.services.geo_service import GeoService
from app.schemas.schemas import LeadCreateIn, LeadCreateOut
from app.core.security import rate_limiter

router = APIRouter(prefix="/leads", tags=["Captura de Leads & Habeas Data"])

@router.post("/registrar", response_model=LeadCreateOut)
def registrar_lead(
    lead_data: LeadCreateIn,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Módulo B: Captura de Lead con verificación de Habeas Data (Ley 1581) y Rate Limiting.
    Retorna el Session Token criptográfico que desbloquea la descarga y la herramienta de Upsell.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Verificación de Rate Limiting
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Ha excedido el número de solicitudes permitidas. Por favor espere un minuto antes de reintentar."
        )

    service = LeadsService(db)
    result = service.registrar_lead(lead_data, client_ip)
    return result

@router.get("/descargar-reporte")
def descargar_reporte(
    token: str = Query(..., description="Token de desbloqueo obtenido al registrarse"),
    municipio_id: Optional[int] = Query(1),
    ambito: Optional[str] = Query("Urbano"),
    db: Session = Depends(get_db)
):
    """
    Descarga el reporte diagnóstico consolidado en formato JSON estructurado
    para directivos docentes autorizados.
    """
    leads_service = LeadsService(db)
    lead = leads_service.obtener_lead_por_token(token)

    demografia_service = DemografiaService(db)
    censo = demografia_service.consultar_censo_demografico(None, municipio_id, ambito)

    geo_service = GeoService(db)
    oferta = geo_service.get_colegios_y_demanda_en_radio(
        censo["latitud"], censo["longitud"], 5.0, municipio_id
    )

    reporte_payload = {
        "titulo": "EDUDEMIA COLOMBIA - INFORME DIAGNÓSTICO EJECUTIVO",
        "beneficiario": {
            "nombre": lead.nombre,
            "correo": lead.correo_institucional,
            "fecha_emision": lead.fecha_registro.isoformat() if lead.fecha_registro else ""
        },
        "censo_demografico": censo,
        "analisis_geoespacial_5km": {
            "total_colegios_en_radio": oferta["total_colegios"],
            "oficiales": oferta["colegios_oficiales"],
            "no_oficiales": oferta["colegios_no_oficiales"],
            "familias_buscando_cupo": oferta["total_estudiantes_buscando"],
            "colegios_destacados": oferta["colegios"][:5]
        },
        "aviso_legal": "Datos procesados conforme a la Ley 1581 de 2012 y proyecciones demográficas DANE."
    }

    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', censo.get('municipio_nombre', 'Zona'))
    filename = f"Edudemia_Reporte_{safe_name}.json"

    content_bytes = json.dumps(reporte_payload, indent=2, ensure_ascii=False)
    return Response(
        content=content_bytes,
        media_type="application/json; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
