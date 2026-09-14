from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Departamento, Municipio, DemografiaNatalidad

class DemografiaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_departamentos(self) -> List[Departamento]:
        return self.db.query(Departamento).order_by(Departamento.nombre).all()

    def get_municipios_by_depto(self, departamento_id: int) -> List[Municipio]:
        return self.db.query(Municipio).filter(Municipio.departamento_id == departamento_id).order_by(Municipio.nombre).all()

    def get_municipio_by_id(self, municipio_id: int) -> Optional[Municipio]:
        return self.db.query(Municipio).filter(Municipio.id == municipio_id).first()

    def get_natalidad_series(self, municipio_id: int, ambito: str) -> List[DemografiaNatalidad]:
        return (
            self.db.query(DemografiaNatalidad)
            .filter(
                DemografiaNatalidad.municipio_id == municipio_id,
                DemografiaNatalidad.ambito == ambito
            )
            .order_by(DemografiaNatalidad.año.asc())
            .all()
        )

    def get_all_ambitos_for_municipio(self, municipio_id: int, año: int) -> List[DemografiaNatalidad]:
        return (
            self.db.query(DemografiaNatalidad)
            .filter(
                DemografiaNatalidad.municipio_id == municipio_id,
                DemografiaNatalidad.año == año
            )
            .all()
        )

