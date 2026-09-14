from sqlalchemy.orm import Session
from pathlib import Path
from app.db.session import engine, Base
from app.models.models import Departamento, Municipio, DemografiaNatalidad, Colegio, MatriculaInternaColegio, EstudianteBuscador
from app.core.config import BASE_DIR

def init_db(db: Session) -> None:
    """Crea las tablas y precarga los datos semilla si la base está vacía."""
    Base.metadata.create_all(bind=engine)
    
    # Verificar si ya existen departamentos cargados
    first_depto = db.query(Departamento).first()
    if first_depto:
        return # Ya inicializado
    
    schema_sql_path = BASE_DIR / "database" / "schema.sql"
    if schema_sql_path.exists():
        with open(schema_sql_path, "r", encoding="utf-8") as f:
            sql_statements = f.read()
        
        # Ejecutar sentencias del script SQL
        with engine.begin() as connection:
            for statement in sql_statements.split(";"):
                stmt = statement.strip()
                if stmt:
                    connection.exec_driver_sql(stmt)
        print("[DB SEEDER] Datos cargados exitosamente desde schema.sql")
    else:
        print("[DB SEEDER] schema.sql no encontrado, omitiendo carga.")

