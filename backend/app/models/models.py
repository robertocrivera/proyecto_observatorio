from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class Departamento(Base):
    __tablename__ = "Departamentos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)

    municipios = relationship("Municipio", back_populates="departamento", cascade="all, delete-orphan")


class Municipio(Base):
    __tablename__ = "Municipios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    departamento_id = Column(Integer, ForeignKey("Departamentos.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    codigo_dane = Column(String(20), unique=True, nullable=False, index=True)
    latitud = Column(Float, default=4.6732)
    longitud = Column(Float, default=-74.1448)

    departamento = relationship("Departamento", back_populates="municipios")
    demografia = relationship("DemografiaNatalidad", back_populates="municipio", cascade="all, delete-orphan")
    colegios = relationship("Colegio", back_populates="municipio", cascade="all, delete-orphan")
    estudiantes_buscadores = relationship("EstudianteBuscador", back_populates="municipio", cascade="all, delete-orphan")


class DemografiaNatalidad(Base):
    __tablename__ = "Demografia_Natalidad"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    municipio_id = Column(Integer, ForeignKey("Municipios.id", ondelete="CASCADE"), nullable=False, index=True)
    ambito = Column(String(50), nullable=False) # 'Urbano', 'Rural Centro', 'Rural Disperso'
    año = Column(Integer, nullable=False)
    nacimientos_registrados = Column(Integer, nullable=False)
    proyeccion_poblacion_0_5_años = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("municipio_id", "ambito", "año", name="uq_mun_ambito_año"),
    )

    municipio = relationship("Municipio", back_populates="demografia")


class Colegio(Base):
    __tablename__ = "Colegios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    municipio_id = Column(Integer, ForeignKey("Municipios.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    sector = Column(String(20), nullable=False) # 'Oficial', 'No Oficial'
    ambito = Column(String(50), nullable=False) # 'Urbano', 'Rural Centro', 'Rural Disperso'
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    direccion = Column(String(255), nullable=True)

    municipio = relationship("Municipio", back_populates="colegios")
    matricula_interna = relationship("MatriculaInternaColegio", back_populates="colegio", cascade="all, delete-orphan")
    leads = relationship("LeadDirectivo", back_populates="colegio")


class LeadDirectivo(Base):
    __tablename__ = "Leads_Directivos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    correo_institucional = Column(String(150), nullable=False, index=True)
    colegio_id_opcional = Column(Integer, ForeignKey("Colegios.id", ondelete="SET NULL"), nullable=True)
    fecha_registro = Column(DateTime, default=get_utc_now)
    tratamiento_datos_aceptado = Column(Boolean, default=True, nullable=False)
    token_descarga = Column(String(100), nullable=True)
    ip_origen = Column(String(45), nullable=True)

    colegio = relationship("Colegio", back_populates="leads")


class MatriculaInternaColegio(Base):
    __tablename__ = "Matricula_Interna_Colegio"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    colegio_id = Column(Integer, ForeignKey("Colegios.id", ondelete="CASCADE"), nullable=False, index=True)
    año = Column(Integer, nullable=False)
    grado = Column(String(50), nullable=False) # 'Transición', 'Primaria', etc.
    numero_estudiantes = Column(Integer, nullable=False)

    colegio = relationship("Colegio", back_populates="matricula_interna")


class EstudianteBuscador(Base):
    __tablename__ = "Estudiantes_Buscadores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    municipio_id = Column(Integer, ForeignKey("Municipios.id", ondelete="CASCADE"), nullable=False, index=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    grado_interes = Column(String(50), nullable=False)
    fecha_consulta = Column(DateTime, default=get_utc_now)

    municipio = relationship("Municipio", back_populates="estudiantes_buscadores")
