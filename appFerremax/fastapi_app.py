import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PaginaFerremax.settings')
django.setup()

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List
import pathlib

# Import Django models
from appFerremax.models import Empleado

# Create FastAPI app
app = FastAPI(title="Ferremax API", 
             description="API para acceder a datos de empleados de Ferremax",
             version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to only allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic model for employee response
class EmpleadoResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: str
    sucursal: str
    cargo: str
    
    class Config:
        orm_mode = True

# API endpoints
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Ferremax"}

@app.get("/api/empleados/", response_model=List[EmpleadoResponse])
async def get_empleados():
    try:
        empleados = Empleado.objects.select_related('sucursal', 'cargo').all()
        
        # Format response
        response = []
        for emp in empleados:
            response.append(
                EmpleadoResponse(
                    id=emp.id_empleado,
                    nombre=emp.nombre_empleado,
                    apellido=emp.apellido_empleado,
                    correo=emp.correo,
                    sucursal=emp.sucursal.nombre_sucursal,
                    cargo=emp.cargo.nombre_cargo
                )
            )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving employees: {str(e)}")

@app.get("/api/empleados/{empleado_id}", response_model=EmpleadoResponse)
async def get_empleado(empleado_id: int):
    try:
        empleado = Empleado.objects.select_related('sucursal', 'cargo').get(id_empleado=empleado_id)
        
        return EmpleadoResponse(
            id=empleado.id_empleado,
            nombre=empleado.nombre_empleado,
            apellido=empleado.apellido_empleado,
            correo=empleado.correo,
            sucursal=empleado.sucursal.nombre_sucursal,
            cargo=empleado.cargo.nombre_cargo
        )
    except Empleado.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Employee with ID {empleado_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving employee: {str(e)}")

# Serve HTML file
@app.get("/empleados")
async def get_empleados_page():
    return HTMLResponse(open("static/empleados.html").read())

# Serve JS and CSS files
@app.get("/static/{file_path:path}")
async def serve_static_file(file_path: str):
    file_path = pathlib.Path("static") / file_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# If running this file directly, start the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # Mount static files directories
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")), name="static")
    
    # Add route to serve the HTML page
    @app.get("/empleados-web", response_class=HTMLResponse)
    async def get_empleados_page():
        html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "Home", "empleados_api.html")
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
                # Replace the Django URL tag with an actual URL
                html_content = html_content.replace("{% url 'index' %}", "/")
                return HTMLResponse(content=html_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading HTML template: {str(e)}")
    
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
