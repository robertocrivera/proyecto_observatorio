from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import secrets

router = APIRouter(prefix="/suscripcion", tags=["Suscripciones & Paywall COP"])

PLANES_COP = {
    "mensual": {
        "id": "mensual",
        "nombre": "Plan Mensual",
        "precio_cop": 189000,
        "precio_formateado": "$189.000 COP",
        "frecuencia": "Facturación mensual recurrente",
        "ahorro": "Sin permanencia",
        "dias_vigencia": 30,
        "caracteristicas": [
            "Motor de recomendaciones prescriptivas para 1 sede",
            "Cruce automático de matrícula con cohorte DANE",
            "Alertas demográficas básicas",
            "Soporte por correo electrónico"
        ]
    },
    "trimestral": {
        "id": "trimestral",
        "nombre": "Plan Trimestral Pro",
        "precio_cop": 489000,
        "precio_formateado": "$489.000 COP",
        "frecuencia": "Facturación cada 3 meses ($163.000 COP/mes)",
        "ahorro": "Ahorre 14%",
        "recomendado": True,
        "dias_vigencia": 90,
        "caracteristicas": [
            "Todo lo del Plan Mensual",
            "Acceso ilimitado a mapas Web GIS (radio de 5 km)",
            "Mapeo de demanda activa de familias buscando cupo",
            "Descargas ejecutivas ilimitadas en formato PDF/JSON",
            "Hasta 3 sedes institucionales incluidas"
        ]
    },
    "anual": {
        "id": "anual",
        "nombre": "Plan Anual Institucional",
        "precio_cop": 1690000,
        "precio_formateado": "$1.690.000 COP",
        "frecuencia": "Facturación anual ($140.833 COP/mes)",
        "ahorro": "Ahorre 25%",
        "mejor_valor": True,
        "dias_vigencia": 365,
        "caracteristicas": [
            "Todo lo del Plan Trimestral",
            "Sedes ilimitadas para todo el municipio",
            "Acompañamiento personalizado de consultor demográfico",
            "Informes listos para Consejo Directivo y Secretaría de Educación",
            "Prioridad máxima en soporte 24/7"
        ]
    }
}

class SuscripcionSimulacionIn(BaseModel):
    plan_id: str = Field(..., description="mensual, trimestral o anual")
    colegio_nombre: str = Field(..., min_length=3)
    correo_directivo: str = Field(...)
    metodo_pago: str = Field("PSE", description="PSE, TARJETA o FACTURA_INSTITUCIONAL")
    banco_o_franquicia: Optional[str] = "Bancolombia"

class SuscripcionSimulacionOut(BaseModel):
    success: bool
    mensaje: str
    subscription_token: str
    plan_id: str
    plan_nombre: str
    precio_cop: int
    precio_formateado: str
    metodo_pago: str
    banco_o_franquicia: Optional[str]
    fecha_inicio: str
    fecha_vencimiento: str
    colegio_nombre: str

@router.get("/planes")
def obtener_planes():
    """Retorna los planes de suscripción vigentes en Pesos Colombianos (COP)."""
    return list(PLANES_COP.values())

@router.post("/activar-simulacion", response_model=SuscripcionSimulacionOut)
def activar_suscripcion_simulada(payload: SuscripcionSimulacionIn):
    """
    Simula el checkout y la activación inmediata de un plan de suscripción institucional en COP.
    Genera una licencia criptográfica que desbloquea el Motor Prescriptivo.
    """
    plan = PLANES_COP.get(payload.plan_id.lower())
    if not plan:
        raise HTTPException(status_code=400, detail="Plan de suscripción no válido. Elija mensual, trimestral o anual.")

    now = datetime.now(timezone.utc)
    vencimiento = now + timedelta(days=plan["dias_vigencia"])
    token_licencia = f"SUB-COP-{secrets.token_hex(6).upper()}-{int(now.timestamp())}"

    return {
        "success": True,
        "mensaje": f"Suscripción al {plan['nombre']} activada con éxito en pesos colombianos.",
        "subscription_token": token_licencia,
        "plan_id": plan["id"],
        "plan_nombre": plan["nombre"],
        "precio_cop": plan["precio_cop"],
        "precio_formateado": plan["precio_formateado"],
        "metodo_pago": payload.metodo_pago,
        "banco_o_franquicia": payload.banco_o_franquicia,
        "fecha_inicio": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "fecha_vencimiento": vencimiento.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "colegio_nombre": payload.colegio_nombre
    }

