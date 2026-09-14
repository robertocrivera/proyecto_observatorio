import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.colegios_repo import ColegiosRepository
from app.repositories.demografia_repo import DemografiaRepository

class GeoService:
    EARTH_RADIUS_KM = 6371.0 # Radio medio de la Tierra en kilómetros

    @classmethod
    def haversine_distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia ortodrómica entre dos coordenadas geográficas
        utilizando la fórmula de Haversine.
        """
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(cls.EARTH_RADIUS_KM * c, 2)

    def __init__(self, db: Session):
        self.colegios_repo = ColegiosRepository(db)
        self.demografia_repo = DemografiaRepository(db)

    def get_colegios_y_demanda_en_radio(
        self,
        lat: float,
        lon: float,
        radio_km: float = 5.0,
        municipio_id: int = 1
    ) -> Dict[str, Any]:
        """
        Retorna colegios y estudiantes con intención de cupo en un radio dinámico (por defecto 5 km).
        """
        municipio = self.demografia_repo.get_municipio_by_id(municipio_id)
        mun_nombre = municipio.nombre if municipio else "Zona Consultada"

        # 1. Filtrar colegios
        todos_colegios = self.colegios_repo.get_all_colegios()
        colegios_en_radio = []
        oficiales = 0
        no_oficiales = 0

        for col in todos_colegios:
            dist = self.haversine_distance(lat, lon, col.latitud, col.longitud)
            if dist <= radio_km:
                col_dict = {
                    "id": col.id,
                    "nombre": col.nombre,
                    "sector": col.sector,
                    "ambito": col.ambito,
                    "latitud": col.latitud,
                    "longitud": col.longitud,
                    "direccion": col.direccion,
                    "distancia_km": dist
                }
                colegios_en_radio.append(col_dict)
                if col.sector == "Oficial":
                    oficiales += 1
                else:
                    no_oficiales += 1

        colegios_en_radio.sort(key=lambda x: x["distancia_km"])

        # 2. Filtrar estudiantes buscadores de cupos
        todos_buscadores = self.colegios_repo.get_all_estudiantes_buscadores()
        buscadores_en_radio = []
        demanda_grados: Dict[str, int] = {}

        for est in todos_buscadores:
            dist = self.haversine_distance(lat, lon, est.latitud, est.longitud)
            if dist <= radio_km:
                buscadores_en_radio.append({
                    "id": est.id,
                    "latitud": est.latitud,
                    "longitud": est.longitud,
                    "grado_interes": est.grado_interes,
                    "distancia_km": dist
                })
                demanda_grados[est.grado_interes] = demanda_grados.get(est.grado_interes, 0) + 1

        buscadores_en_radio.sort(key=lambda x: x["distancia_km"])

        return {
            "centro_lat": lat,
            "centro_lng": lon,
            "radio_km": radio_km,
            "municipio_nombre": mun_nombre,
            "total_colegios": len(colegios_en_radio),
            "colegios_oficiales": oficiales,
            "colegios_no_oficiales": no_oficiales,
            "colegios": colegios_en_radio,
            "total_estudiantes_buscando": len(buscadores_en_radio),
            "estudiantes_buscadores": buscadores_en_radio,
            "demanda_por_grado": demanda_grados
        }

