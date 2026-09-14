from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.leads_repo import LeadsRepository
from app.core.security import InputSanitizer, SecurityManager
from app.schemas.schemas import LeadCreateIn

class LeadsService:
    def __init__(self, db: Session):
        self.leads_repo = LeadsRepository(db)

    def registrar_lead(self, lead_data: LeadCreateIn, client_ip: str) -> Dict[str, Any]:
        # 1. Sanitizar campos
        nombre_limpio = InputSanitizer.sanitize_text(lead_data.nombre)
        correo_limpio = InputSanitizer.sanitize_text(lead_data.correo_institucional).lower()

        # 2. Validar formato de correo
        if not InputSanitizer.is_valid_email(correo_limpio):
            raise HTTPException(
                status_code=400,
                detail="El formato del correo institucional es inválido. Verifique e intente nuevamente."
            )

        # 3. Validar Habeas Data (Ley 1581 de 2012)
        if not lead_data.tratamiento_datos_aceptado:
            raise HTTPException(
                status_code=400,
                detail="Debe aceptar la política de tratamiento de datos personales conforme a la Ley Estatutaria 1581 de 2012."
            )

        # 4. Generar token de sesión seguro para el desbloqueo de reporte y upsell
        token_descarga = SecurityManager.generate_session_token(correo_limpio)

        # 5. Persistir lead en la base de datos
        nuevo_lead = self.leads_repo.create_lead(
            nombre=nombre_limpio,
            correo_institucional=correo_limpio,
            tratamiento_datos_aceptado=lead_data.tratamiento_datos_aceptado,
            token_descarga=token_descarga,
            colegio_id_opcional=lead_data.colegio_id_opcional,
            ip_origen=client_ip
        )

        return {
            "success": True,
            "mensaje": f"Lead institucional registrado exitosamente para {nombre_limpio}.",
            "lead_id": nuevo_lead.id,
            "token_descarga": token_descarga,
            "download_url": f"/api/v1/leads/descargar-reporte?token={token_descarga}"
        }

    def obtener_lead_por_token(self, token: str):
        lead = self.leads_repo.get_lead_by_token(token)
        if not lead:
            raise HTTPException(status_code=403, detail="Token de sesión o descarga inválido o caducado.")
        return lead

