from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Colegio, EstudianteBuscador

class ColegiosRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_colegios_by_municipio(self, municipio_id: int) -> List[Colegio]:
        return self.db.query(Colegio).filter(Colegio.municipio_id == municipio_id).all()

    def get_all_colegios(self) -> List[Colegio]:
        return self.db.query(Colegio).all()

    def get_colegio_by_id(self, colegio_id: int) -> Optional[Colegio]:
        return self.db.query(Colegio).filter(Colegio.id == colegio_id).first()

    def count_colegios_by_sector(self, municipio_id: int, sector: str) -> int:
        return (
            self.db.query(Colegio)
            .filter(Colegio.municipio_id == municipio_id, Colegio.sector == sector)
            .count()
        )

    def get_estudiantes_buscadores_by_municipio(self, municipio_id: int) -> List[EstudianteBuscador]:
        return (
            self.db.query(EstudianteBuscador)
            .filter(EstudianteBuscador.municipio_id == municipio_id)
            .all()
        )

    def get_all_estudiantes_buscadores(self) -> List[EstudianteBuscador]:
        return self.db.query(EstudianteBuscador).all()

