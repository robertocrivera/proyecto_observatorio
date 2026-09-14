from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Esquemas de Departamentos y Municipios ---
class DepartamentoOut(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class MunicipioOut(BaseModel):
    id: int
    departamento_id: int
    nombre: str
    codigo_dane: str
    latitud: float
    longitud: float

    class Config:
        from_attributes = True

# --- Esquemas de Demografía y Censo Cruzado ---
class DemografiaItem(BaseModel):
    año: int
    nacimientos: int
    proyeccion_0_5: int

class DemografiaResponseOut(BaseModel):
    departamento_id: int
    departamento_nombre: str
    municipio_id: int
    municipio_nombre: str
    ambito: str
    serie_historica: List[DemografiaItem]
    variacion_porcentual: float
    resumen_ambito: Dict[str, float]
    total_colegios_oficiales: int
    total_colegios_no_oficiales: int
    radio_cobertura_km: float = 5.0

# --- Esquemas de Colegios y Geoespacial ---
class ColegioOut(BaseModel):
    id: int
    nombre: str
    sector: str
    ambito: str
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    distancia_km: Optional[float] = None

    class Config:
        from_attributes = True

class EstudianteBuscadorOut(BaseModel):
    id: int
    latitud: float
    longitud: float
    grado_interes: str
    distancia_km: Optional[float] = None

    class Config:
        from_attributes = True

class GeoRadioResponseOut(BaseModel):
    centro_lat: float
    centro_lng: float
    radio_km: float
    municipio_nombre: str
    total_colegios: int
    colegios_oficiales: int
    colegios_no_oficiales: int
    colegios: List[ColegioOut]
    total_estudiantes_buscando: int
    estudiantes_buscadores: List[EstudianteBuscadorOut]
    demanda_por_grado: Dict[str, int]

# --- Esquemas de Leads (Lead Magnet y Habeas Data) ---
class LeadCreateIn(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    correo_institucional: str = Field(..., max_length=150)
    tratamiento_datos_aceptado: bool = Field(..., description="Debe aceptar la Ley 1581 de Habeas Data")
    colegio_id_opcional: Optional[int] = None
    municipio_id: Optional[int] = None
    ambito: Optional[str] = None

    @field_validator("tratamiento_datos_aceptado")
    @classmethod
    def validar_habeas_data(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Es obligatorio autorizar el tratamiento de datos personales conforme a la Ley 1581.")
        return v

class LeadCreateOut(BaseModel):
    success: bool
    mensaje: str
    lead_id: int
    token_descarga: str
    download_url: str

# --- Esquemas de Comparativa Estratégica y Recomendaciones ---
class MatriculaItemIn(BaseModel):
    año: int
    grado: str
    numero_estudiantes: int

class EstrategiaCompararIn(BaseModel):
    municipio_id: int
    colegio_nombre: Optional[str] = "Mi Institución Educativa"
    sector: Optional[str] = "No Oficial"
    ambito: Optional[str] = "Urbano"
    matricula_historica: List[MatriculaItemIn]

class RecomendacionEstrategica(BaseModel):
    tipo: str # 'ALERTA_CRITICA', 'OPORTUNIDAD_MERCADO', 'OPTIMIZACION_OPERATIVA'
    titulo: str
    descripcion: str
    impacto_estimado: str

class EstrategiaResponseOut(BaseModel):
    colegio_nombre: str
    variacion_matricula_institucional: float
    variacion_natalidad_territorial: float
    colegios_competencia_radio_5km: int
    estudiantes_buscando_cupo_5km: int
    recomendaciones: List[RecomendacionEstrategica]

