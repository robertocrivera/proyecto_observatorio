from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.demografia_repo import DemografiaRepository
from app.repositories.colegios_repo import ColegiosRepository
from app.services.geo_service import GeoService
from app.schemas.schemas import EstrategiaCompararIn, RecomendacionEstrategica

class EstrategiaService:
    def __init__(self, db: Session):
        self.db = db
        self.demografia_repo = DemografiaRepository(db)
        self.colegios_repo = ColegiosRepository(db)
        self.geo_service = GeoService(db)

    def comparar_y_diagnosticar(self, data: EstrategiaCompararIn) -> Dict[str, Any]:
        municipio = self.demografia_repo.get_municipio_by_id(data.municipio_id)
        if not municipio:
            # Fallback al primer municipio
            muns = self.demografia_repo.get_municipios_by_depto(1)
            municipio = muns[0]

        # 1. Calcular variación en la matrícula interna institucional enviada
        matricula = data.matricula_historica
        variacion_matricula = 0.0
        if matricula and len(matricula) >= 2:
            # Ordenar por año
            sorted_mat = sorted(matricula, key=lambda x: x.año)
            primer_año_val = sorted_mat[0].numero_estudiantes
            ultimo_año_val = sorted_mat[-1].numero_estudiantes
            if primer_año_val > 0:
                variacion_matricula = round(((ultimo_año_val - primer_año_val) / primer_año_val) * 100.0, 1)

        # 2. Obtener variación demográfica territorial (DANE)
        serie_dane = self.demografia_repo.get_natalidad_series(municipio.id, data.ambito or "Urbano")
        variacion_dane = 0.0
        if len(serie_dane) >= 2:
            ini_dane = serie_dane[0].nacimientos_registrados
            fin_dane = serie_dane[-1].nacimientos_registrados
            if ini_dane > 0:
                variacion_dane = round(((fin_dane - ini_dane) / ini_dane) * 100.0, 1)

        # 3. Análisis geoespacial de competencia y buscadores en 5 km
        geo_analisis = self.geo_service.get_colegios_y_demanda_en_radio(
            lat=municipio.latitud,
            lon=municipio.longitud,
            radio_km=5.0,
            municipio_id=municipio.id
        )

        num_competencia = geo_analisis["total_colegios"]
        num_buscadores = geo_analisis["total_estudiantes_buscando"]
        demanda_grados = geo_analisis["demanda_por_grado"]

        # 4. Motor de Recomendaciones Prescriptivas
        recomendaciones: List[RecomendacionEstrategica] = []

        # Recomendación 1: Alerta Crítica Demográfica vs Preescolar / Primaria
        if variacion_dane < -10 or variacion_matricula < -5:
            recomendaciones.append(RecomendacionEstrategica(
                tipo="ALERTA_CRITICA",
                titulo="Transición Demográfica en Grados Iniciales",
                descripcion=(
                    f"Atención: La tasa de nacimientos en el ámbito {data.ambito} de {municipio.nombre} "
                    f"ha descendido un {abs(variacion_dane)}% en los últimos años. Su matrícula reporta una tendencia de "
                    f"{variacion_matricula}%. Se recomienda reestructurar los cupos de educación inicial y proyectar la "
                    f"fusión de grupos pequeños hacia educación media técnica y programas extra-edad con transporte regional."
                ),
                impacto_estimado="Mitigación de hasta un 25% en costos operativos de aulas subutilizadas"
            ))
        else:
            recomendaciones.append(RecomendacionEstrategica(
                tipo="ALERTA_CRITICA",
                titulo="Estabilidad Relativa con Riesgo de Reemplazo Generacional",
                descripcion=(
                    f"En {municipio.nombre}, la cohorte infantil presenta una variación de {variacion_dane}%. "
                    f"Mantenga un control estricto de retención escolar en los grados puente (Transición a 1° y 5° a 6°)."
                ),
                impacto_estimado="Retención de hasta un 92% de la cohorte en transición"
            ))

        # Recomendación 2: Oportunidad de Mercado / Captación en Radio 5 km
        grados_top = list(demanda_grados.keys())[:2]
        grados_str = " y ".join(grados_top) if grados_top else "Transición y Primaria"
        recomendaciones.append(RecomendacionEstrategica(
            tipo="OPORTUNIDAD_MERCADO",
            titulo="Captura de Demanda Activa en Radio de Proximidad (5 km)",
            descripcion=(
                f"Existen {num_buscadores} familias activamente geolocalizadas a menos de 5 km buscando cupos en {grados_str}. "
                f"Frente a una competencia de {num_competencia} colegios ({geo_analisis['colegios_oficiales']} oficiales y "
                f"{geo_analisis['colegios_no_oficiales']} no oficiales), se recomienda lanzar una campaña focalizada de "
                f"puertas abiertas y destacar diferenciales de jornada única o robótica escolar."
            ),
            impacto_estimado=f"Atracción estimada de entre {max(5, num_buscadores * 2)} y {max(15, num_buscadores * 4)} matrículas nuevas"
        ))

        # Recomendación 3: Optimización Curricular y Capacidad Instalada
        recomendaciones.append(RecomendacionEstrategica(
            tipo="OPTIMIZACION_OPERATIVA",
            titulo="Reconversión de Capacidad y Alianzas Formativas",
            descripcion=(
                f"Reconvertir aulas tradicionales en laboratorios Maker, aulas STEAM y programas de articulación "
                f"con el SENA / educación terciaria. El envejecimiento poblacional exige elevar el valor percibido del grado 10° y 11° "
                f"para evitar la deserción hacia validaciones o colegios nocturnos."
            ),
            impacto_estimado="Aumento del 18% en el ticket promedio institucional y mayor fidelización"
        ))

        return {
            "colegio_nombre": data.colegio_nombre or "Mi Institución Educativa",
            "variacion_matricula_institucional": variacion_matricula,
            "variacion_natalidad_territorial": variacion_dane,
            "colegios_competencia_radio_5km": num_competencia,
            "estudiantes_buscando_cupo_5km": num_buscadores,
            "recomendaciones": [r.model_dump() for r in recomendaciones]
        }

