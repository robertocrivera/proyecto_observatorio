from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import MatriculaInternaColegio

class EstrategiaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_matricula_by_colegio(self, colegio_id: int) -> List[MatriculaInternaColegio]:
        return (
            self.db.query(MatriculaInternaColegio)
            .filter(MatriculaInternaColegio.colegio_id == colegio_id)
            .order_by(MatriculaInternaColegio.año.asc())
            .all()
        )

    def save_matricula_record(self, colegio_id: int, año: int, grado: str, numero_estudiantes: int) -> MatriculaInternaColegio:
        record = MatriculaInternaColegio(
            colegio_id=colegio_id,
            año=año,
            grado=grado,
            numero_estudiantes=numero_estudiantes
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

