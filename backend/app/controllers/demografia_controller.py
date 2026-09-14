from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.demografia_service import DemografiaService
from app.schemas.schemas import DepartamentoOut, MunicipioOut, DemografiaResponseOut

router = APIRouter(prefix="/demografia", tags=["Demografía y Censo DANE"])

@router.get("/departamentos", response_model=List[DepartamentoOut])
def get_departamentos(db: Session = Depends(get_db)):
    """Obtiene el listado de departamentos de Colombia registrados."""
    service = DemografiaService(db)
    return service.get_departamentos()

@router.get("/municipios", response_model=List[MunicipioOut])
def get_municipios(
    departamento_id: int = Query(..., description="ID del departamento a filtrar"),
    db: Session = Depends(get_db)
):
    """Obtiene los municipios pertenecientes a un departamento."""
    service = DemografiaService(db)
    return service.get_municipios(departamento_id)

@router.get("/consulta", response_model=DemografiaResponseOut)
def consultar_censo(
    departamento_id: Optional[int] = Query(None, description="ID del departamento"),
    municipio_id: Optional[int] = Query(None, description="ID del municipio"),
    ambito: Optional[str] = Query("Urbano", description="Ámbito territorial: Urbano, Rural Centro o Rural Disperso"),
    db: Session = Depends(get_db)
):
    """
    Módulo A: Censo Demográfico Cruzado.
    Calcula en tiempo real la serie de natalidad, variación porcentual y oferta de colegios.
    """
    service = DemografiaService(db)
    return service.consultar_censo_demografico(departamento_id, municipio_id, ambito)

