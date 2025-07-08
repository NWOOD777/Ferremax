from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# Crea las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Empleados",
    description="Una API para gestionar empleados.",
    version="1.0.0",
)

# --- Endpoint para obtener la lista de empleados ---
@app.get("/empleados/", response_model=List[schemas.Empleado], tags=["Empleados"])
def read_empleados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Recupera una lista de empleados desde la base de datos.
    """
    empleados = crud.get_empleados(db, skip=skip, limit=limit)
    return empleados


# --- Endpoint de bienvenida ---
@app.get("/", tags=["General"])
def read_root():
    return {"mensaje": "Bienvenido a la API de Empleados. Visita /docs para ver la documentación."}


