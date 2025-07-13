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
        empleado = Empleado.objects.filter(cargo__nombre_cargo='Vendedor').first() or Empleado.objects.first()
        if not empleado:
            print("No se encontraron empleados, no se puede asignar un creador al producto.")
            return
        
        # Preparamos directorios
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        static_root = getattr(settings, 'STATIC_ROOT', None)
        base_dir = getattr(settings, 'BASE_DIR', None)
        
        # Aseguramos que la carpeta productos existe
        os.makedirs(os.path.join(media_root, 'productos'), exist_ok=True)
        
        # Buscar imágenes en la carpeta static/assets/images/imagenes_ferremas
        ferremas_images_dir = os.path.join(base_dir, 'appFerremax', 'static', 'assets', 'images', 'imagenes_ferremas')
        print(f"Buscando imágenes en: {ferremas_images_dir}")
        image_files = []
        
        if os.path.exists(ferremas_images_dir):
            print(f"La carpeta de imágenes existe")
            # Listar todas las imágenes .jpg y .png en la carpeta
            image_files = [f for f in os.listdir(ferremas_images_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            print(f"Imágenes encontradas: {len(image_files)}")
            if image_files:
                print(f"Ejemplos: {', '.join(image_files[:3])}")
        else:
            print(f"La carpeta de imágenes NO existe en la ruta especificada")
        
        if not image_files:
            # Si no hay imágenes, usamos una imagen por defecto en base64
            print("No se encontraron imágenes en la carpeta. Usando imagen por defecto.")
            img_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
            default_image_path = os.path.join(media_root, 'productos', 'producto_default.png')
            with open(default_image_path, 'wb') as f:
                f.write(img_data)
            image_paths = ['productos/producto_default.png'] * 3  # Usar la misma imagen para los 3 productos
        else:
            # Copiar hasta 3 imágenes diferentes a la carpeta de productos
            image_paths = []
            for i, img_name in enumerate(image_files[:3]):  # Tomar hasta 3 imágenes
                src_path = os.path.join(ferremas_images_dir, img_name)
                dest_name = f'producto_migracion_{i+1}_{img_name}'
                dest_path = os.path.join(media_root, 'productos', dest_name)
                
                # Copiar la imagen al directorio de media
                import shutil
                try:
                    # Asegurarnos que el directorio destino existe
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"Imagen copiada correctamente: {src_path} → {dest_path}")
                except Exception as e:
                    print(f"Error al copiar imagen: {e}")
                
                image_paths.append(f'productos/{dest_name}')
            
            # Si hay menos de 3 imágenes, repetir la última
            while len(image_paths) < 3:
                image_paths.append(image_paths[-1])
        
        # Crear 3 productos con diferentes stocks
        from decimal import Decimal
        
        # Producto 1 - Stock 50
        Producto.objects.create(
            nombre_producto="Martillo Profesional",
            descripcion="Martillo de carpintero con mango ergonómico y cabeza de acero reforzado",
            marca="Ferremax Tools",
            precio_unitario=Decimal('12990.00'),
            stock_total=50,
            sucursal=sucursal,
            imagen=image_paths[0],
            creado_por=empleado
        )
        
        # Producto 2 - Stock 0
        Producto.objects.create(
            nombre_producto="Taladro Inalámbrico",
            descripcion="Taladro inalámbrico recargable con batería de litio y maletín de transporte",
            marca="PowerMax",
            precio_unitario=Decimal('45990.00'),
            stock_total=0,
            sucursal=sucursal,
            imagen=image_paths[1],
            creado_por=empleado
        )
        
        # Producto 3 - Stock 7
        Producto.objects.create(
            nombre_producto="Set de Destornilladores",
            descripcion="Juego de 8 destornilladores de precisión con diferentes puntas y tamaños",
            marca="ToolPro",
            precio_unitario=Decimal('9990.00'),
            stock_total=7,
            sucursal=sucursal,
            imagen=image_paths[2],
            creado_por=empleado
        )
        
        print("Se han creado 3 productos con diferentes niveles de stock.")
    
    except Exception as e:
        print(f"Error al crear el producto por defecto: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0011_auto_20250710_1948'),
    ]
    
    operations = [
        migrations.RunPython(crear_producto_por_defecto),
    ]
