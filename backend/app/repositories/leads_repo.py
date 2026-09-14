from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import LeadDirectivo

class LeadsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_lead(
        self,
        nombre: str,
        correo_institucional: str,
        tratamiento_datos_aceptado: bool,
        token_descarga: str,
        colegio_id_opcional: Optional[int] = None,
        ip_origen: Optional[str] = None
    ) -> LeadDirectivo:
        lead = LeadDirectivo(
            nombre=nombre,
            correo_institucional=correo_institucional,
            tratamiento_datos_aceptado=tratamiento_datos_aceptado,
            token_descarga=token_descarga,
            colegio_id_opcional=colegio_id_opcional,
            ip_origen=ip_origen
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_lead_by_email(self, email: str) -> Optional[LeadDirectivo]:
        return self.db.query(LeadDirectivo).filter(LeadDirectivo.correo_institucional == email).first()

    def get_lead_by_token(self, token: str) -> Optional[LeadDirectivo]:
        return self.db.query(LeadDirectivo).filter(LeadDirectivo.token_descarga == token).first()

    def list_all_leads(self) -> List[LeadDirectivo]:
        return self.db.query(LeadDirectivo).order_by(LeadDirectivo.fecha_registro.desc()).all()

