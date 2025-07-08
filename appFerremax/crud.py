from sqlalchemy.orm import Session

from . import models

def get_empleados(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de empleados con paginación."""
    return db.query(models.Empleado).offset(skip).limit(limit).all()


