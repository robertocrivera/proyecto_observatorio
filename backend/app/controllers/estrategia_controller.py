from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.estrategia_service import EstrategiaService
from app.schemas.schemas import EstrategiaCompararIn, EstrategiaResponseOut

router = APIRouter(prefix="/estrategia", tags=["Estrategia Comparativa & Diagnóstico Prescriptivo"])

@router.post("/comparar", response_model=EstrategiaResponseOut)
def comparar_matricula(
    payload: EstrategiaCompararIn,
    db: Session = Depends(get_db)
):
    """
    Módulo C.2: Comparativa y Diagnóstico Prescriptivo.
    Cruza los datos de matrícula institucional con las curvas DANE y la oferta circundante
    para devolver recomendaciones estratégicas accionables.
    """
    service = EstrategiaService(db)
    return service.comparar_y_diagnosticar(payload)

