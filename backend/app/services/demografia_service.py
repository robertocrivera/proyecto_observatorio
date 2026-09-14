from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.repositories.demografia_repo import DemografiaRepository
from app.repositories.colegios_repo import ColegiosRepository
from fastapi import HTTPException

class DemografiaService:
    def __init__(self, db: Session):
        self.demografia_repo = DemografiaRepository(db)
        self.colegios_repo = ColegiosRepository(db)

    def get_departamentos(self):
        return self.demografia_repo.get_departamentos()

    def get_municipios(self, departamento_id: int):
        return self.demografia_repo.get_municipios_by_depto(departamento_id)

    def consultar_censo_demografico(
        self,
        departamento_id: Optional[int],
        municipio_id: Optional[int],
        ambito: Optional[str]
    ) -> Dict[str, Any]:
        # Fallback inteligente si no se envían IDs específicos
        if not municipio_id:
            deptos = self.demografia_repo.get_departamentos()
            if not deptos:
                raise HTTPException(status_code=404, detail="No se encontraron departamentos.")
            depto_id = departamento_id or deptos[0].id
            muns = self.demografia_repo.get_municipios_by_depto(depto_id)
            if not muns:
                raise HTTPException(status_code=404, detail="No se encontraron municipios.")
            municipio = muns[0]
        else:
            municipio = self.demografia_repo.get_municipio_by_id(municipio_id)
            if not municipio:
                raise HTTPException(status_code=404, detail=f"Municipio con id {municipio_id} no encontrado.")

        depto = municipio.departamento
        ambito_seleccionado = ambito if ambito in ["Urbano", "Rural Centro", "Rural Disperso"] else "Urbano"

        # 1. Serie histórica para el ámbito seleccionado
        serie_db = self.demografia_repo.get_natalidad_series(municipio.id, ambito_seleccionado)
        
        # Si no hay datos directos, intentar cargar con Urbano
        if not serie_db:
            serie_db = self.demografia_repo.get_natalidad_series(municipio.id, "Urbano")
            ambito_seleccionado = "Urbano"

        serie_items = [
            {
                "año": s.año,
                "nacimientos": s.nacimientos_registrados,
                "proyeccion_0_5": s.proyeccion_poblacion_0_5_años
            }
            for s in serie_db
        ]

        # 2. Calcular variación porcentual (primer año vs último año)
        variacion_pct = 0.0
        if len(serie_items) >= 2:
            primer_nac = serie_items[0]["nacimientos"]
            ultimo_nac = serie_items[-1]["nacimientos"]
            if primer_nac > 0:
                variacion_pct = round(((ultimo_nac - primer_nac) / primer_nac) * 100.0, 1)

        # 3. Resumen de distribución territorial para el último año disponible
        ultimo_año = serie_items[-1]["año"] if serie_items else 2024
        todos_ambitos = self.demografia_repo.get_all_ambitos_for_municipio(municipio.id, ultimo_año)
        
        total_poblacion_ambitos = sum(a.proyeccion_poblacion_0_5_años for a in todos_ambitos) or 1
        resumen_ambito = {
            "Urbano": 0.0,
            "Rural Centro": 0.0,
            "Rural Disperso": 0.0
        }
        for amb in todos_ambitos:
            pct = round((amb.proyeccion_poblacion_0_5_años / total_poblacion_ambitos) * 100.0, 1)
            if amb.ambito in resumen_ambito:
                resumen_ambito[amb.ambito] = pct

        # 4. Total de colegios oficiales y no oficiales en el municipio
        oficiales = self.colegios_repo.count_colegios_by_sector(municipio.id, "Oficial")
        no_oficiales = self.colegios_repo.count_colegios_by_sector(municipio.id, "No Oficial")

        return {
            "departamento_id": depto.id if depto else 1,
            "departamento_nombre": depto.nombre if depto else "Cundinamarca",
            "municipio_id": municipio.id,
            "municipio_nombre": municipio.nombre,
            "latitud": municipio.latitud,
            "longitud": municipio.longitud,
            "ambito": ambito_seleccionado,
            "serie_historica": serie_items,
            "variacion_porcentual": variacion_pct,
            "resumen_ambito": resumen_ambito,
            "total_colegios_oficiales": oficiales,
            "total_colegios_no_oficiales": no_oficiales,
            "radio_cobertura_km": 5.0
        }

