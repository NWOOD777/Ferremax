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
from typing import List, Optional
import pathlib

# Async support
from asgiref.sync import sync_to_async
import asyncio

# Import Django models
from appFerremax.models import Empleado, Producto

# Create FastAPI app
app = FastAPI(title="Ferremax API", 
             description="API para acceder a datos de empleados y productos de Ferremax",
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
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

# Pydantic model for product response
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    marca: str
    precio: float
    stock: int
    imagen_url: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

# API endpoints
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Ferremax"}

# Función sincrónica para obtener empleados
def get_empleados_sync():
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

@app.get("/api/empleados/", response_model=List[EmpleadoResponse])
async def get_empleados():
    try:
        # Usar sync_to_async para convertir la función sincrónica a asincrónica
        response = await sync_to_async(get_empleados_sync)()
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error detallado al recuperar empleados: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error retrieving employees: {str(e)}")

# Función sincrónica para obtener un empleado individual
def get_empleado_sync(empleado_id: int):
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
        return None  # Manejaremos el 404 en la función asíncrona

@app.get("/api/empleados/{empleado_id}", response_model=EmpleadoResponse)
async def get_empleado(empleado_id: int):
    try:
        # Usar sync_to_async para convertir la función sincrónica a asincrónica
        empleado = await sync_to_async(get_empleado_sync)(empleado_id)
        
        if empleado is None:
            raise HTTPException(status_code=404, detail=f"Employee with ID {empleado_id} not found")
            
        return empleado
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error detallado al recuperar empleado {empleado_id}: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error retrieving employee: {str(e)}")

# Función sincrónica para obtener productos
def get_productos_sync():
    productos = Producto.objects.all()
    
    # Format response
    response = []
    for prod in productos:
        # Manejo de la imagen
        imagen_url = None
        try:
            if prod.imagen:
                # Si es una cadena (ruta relativa)
                if isinstance(prod.imagen, str):
                    imagen_url = f"/media/{prod.imagen}"
                # Si es un objeto ImageField con método url
                elif hasattr(prod.imagen, 'url'):
                    imagen_url = f"/media/{prod.imagen.name}"
                # Si solo tenemos el nombre del archivo
                elif hasattr(prod.imagen, 'name'):
                    imagen_url = f"/media/{prod.imagen.name}"
        except Exception as img_error:
            print(f"Error procesando imagen para producto {prod.id_producto}: {str(img_error)}")
            imagen_url = None
        
        # Intento convertir el precio a float de manera segura
        try:
            precio = float(prod.precio_unitario) if prod.precio_unitario is not None else 0.0
        except (ValueError, TypeError):
            precio = 0.0
            
        # Intento convertir el stock a int de manera segura
        try:
            stock = int(prod.stock_total) if prod.stock_total is not None else 0
        except (ValueError, TypeError):
            stock = 0
            
        try:
            response.append(
                ProductoResponse(
                    id=prod.id_producto,
                    nombre=prod.nombre_producto or "Sin nombre",
                    marca=prod.marca or "Sin marca",
                    precio=precio,
                    stock=stock,
                    imagen_url=imagen_url
                )
            )
        except Exception as item_error:
            print(f"Error creating product response item: {str(item_error)}")
            # Continuar con el siguiente producto en caso de error
            continue
    
    return response

# API endpoints for products
@app.get("/api/productos/", response_model=List[ProductoResponse])
async def get_productos():
    try:
        # Usar sync_to_async para convertir la función sincrónica a asincrónica
        response = await sync_to_async(get_productos_sync)()
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error detallado al recuperar productos: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")

# Función sincrónica para obtener un producto individual
def get_producto_sync(producto_id: int):
    try:
        producto = Producto.objects.get(id_producto=producto_id)
        
        # Manejo de la imagen
        imagen_url = None
        try:
            if producto.imagen:
                # Si es una cadena (ruta relativa)
                if isinstance(producto.imagen, str):
                    imagen_url = f"/media/{producto.imagen}"
                # Si es un objeto ImageField con método url
                elif hasattr(producto.imagen, 'url'):
                    imagen_url = f"/media/{producto.imagen.name}"
                # Si solo tenemos el nombre del archivo
                elif hasattr(producto.imagen, 'name'):
                    imagen_url = f"/media/{producto.imagen.name}"
        except Exception as img_error:
            print(f"Error procesando imagen para producto {producto_id}: {str(img_error)}")
            imagen_url = None
            
        # Intento convertir el precio a float de manera segura
        try:
            precio = float(producto.precio_unitario) if producto.precio_unitario is not None else 0.0
        except (ValueError, TypeError):
            precio = 0.0
            
        # Intento convertir el stock a int de manera segura
        try:
            stock = int(producto.stock_total) if producto.stock_total is not None else 0
        except (ValueError, TypeError):
            stock = 0
            
        return ProductoResponse(
            id=producto.id_producto,
            nombre=producto.nombre_producto or "Sin nombre",
            marca=producto.marca or "Sin marca",
            precio=precio,
            stock=stock,
            imagen_url=imagen_url
        )
    except Producto.DoesNotExist:
        return None  # Manejaremos el 404 en la función asíncrona

@app.get("/api/productos/{producto_id}", response_model=ProductoResponse)
async def get_producto(producto_id: int):
    try:
        # Usar sync_to_async para convertir la función sincrónica a asincrónica
        producto = await sync_to_async(get_producto_sync)(producto_id)
        
        if producto is None:
            raise HTTPException(status_code=404, detail=f"Product with ID {producto_id} not found")
            
        return producto
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error detallado al recuperar producto {producto_id}: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")

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
    
    # Add route to serve the HTML page for employees
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
    
    # Add route to serve the HTML page for products API
    @app.get("/productosapi", response_class=HTMLResponse)
    async def get_productos_api_page():
        html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "Home", "productos_api.html")
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
                # Replace the Django URL tag with an actual URL
                html_content = html_content.replace("{% url 'index' %}", "/")
                return HTMLResponse(content=html_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading HTML template: {str(e)}")
    
    # Add route to serve media files
    @app.get("/media/{file_path:path}")
    async def serve_media_file(file_path: str):
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
        file_path = os.path.join(media_dir, file_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        else:
            # Return a default image or 404
            default_image = os.path.join(media_dir, "default.jpg")
            if os.path.exists(default_image):
                return FileResponse(default_image)
            raise HTTPException(status_code=404, detail="Image not found")
    
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8001, reload=True)
