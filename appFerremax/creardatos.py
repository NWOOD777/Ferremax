# crear_datos.py
from app.database import SessionLocal, engine
from app.models import Empleado, Base

# Crea las tablas
Base.metadata.create_all(bind=engine)

# Abre una sesión
db = SessionLocal()

# Crea algunos empleados de ejemplo
empleados_ejemplo = [
    Empleado(nombre="Ana", apellido="García", puesto="Desarrolladora Backend"),
    Empleado(nombre="Carlos", apellido="Martínez", puesto="Diseñador UX/UI"),
    Empleado(nombre="Sofía", apellido="López", puesto="Jefa de Proyecto"),
]

# Añade los empleados a la sesión y guárdalos en la BD
db.add_all(empleados_ejemplo)
db.commit()

print("Base de datos poblada con datos de ejemplo.")

# Cierra la sesión
db.close()
