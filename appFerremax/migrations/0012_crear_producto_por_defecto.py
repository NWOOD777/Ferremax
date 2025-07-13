from django.db import migrations
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from pathlib import Path
import base64

def crear_producto_por_defecto(apps, schema_editor):
    Producto = apps.get_model('appFerremax', 'Producto')
    Sucursal = apps.get_model('appFerremax', 'Sucursal')
    Empleado = apps.get_model('appFerremax', 'Empleado')
    
    # Verificar si ya existen productos
    # Comentamos esta validación para permitir crear el producto por defecto aunque ya existan otros
    # if Producto.objects.exists():
    #     return
    
    # Obtener la primera sucursal
    try:
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("No se encontraron sucursales, no se puede crear el producto.")
            return
            
        # Obtener un empleado para asociar como creador
        empleado = Empleado.objects.first()
        if not empleado:
            print("No se encontraron empleados, no se puede asignar un creador al producto.")
        
        # Crear una imagen simple para el producto
        # Primero intentamos usar una imagen existente
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        imagen_path = None
        
        # Buscar si hay imágenes en la carpeta productos
        if media_root:
            productos_dir = Path(media_root) / 'productos'
            if productos_dir.exists():
                image_files = list(productos_dir.glob('*.jpg')) + list(productos_dir.glob('*.png'))
                if image_files:
                    imagen_path = str(image_files[0].relative_to(media_root))
        
        # Si no encontramos una imagen, creamos una imagen en base64 (una imagen simple 1x1)
        if not imagen_path:
            # Base64 de un pixel rojo
            img_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
            imagen_path = 'productos/producto_default.png'
            
            # Aseguramos que la carpeta productos existe
            os.makedirs(os.path.join(media_root, 'productos'), exist_ok=True)
            
            # Guardamos la imagen
            with open(os.path.join(media_root, imagen_path), 'wb') as f:
                f.write(img_data)
        
        # Crear el producto por defecto
        from decimal import Decimal
        Producto.objects.create(
            nombre_producto="Martillo profesional",
            descripcion="Martillo de carpintero con mango ergonómico y cabeza de acero reforzado",
            marca="Ferremax Tools",
            precio_unitario=Decimal('12990.00'),  # Usando Decimal explícito para consistencia
            stock_total=50,
            sucursal=sucursal,
            imagen=imagen_path,
            creado_por=empleado
        )
        
        print("Se ha creado un producto por defecto.")
    
    except Exception as e:
        print(f"Error al crear el producto por defecto: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0011_auto_20250710_1948'),
    ]
    
    operations = [
        migrations.RunPython(crear_producto_por_defecto),
    ]
