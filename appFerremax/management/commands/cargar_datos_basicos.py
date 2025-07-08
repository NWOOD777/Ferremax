from django.core.management.base import BaseCommand
from django.core.files import File
from appFerremax.models import Producto, Sucursal
import os

    #Para cargar datos: python manage.py cargar_datos_basicos
    #Para eliminar 
    #Entrar a la terminal del shell: python manage.py shell
    #from appFerremax.models import Producto
    #Producto.objects.filter(nombre_producto="Alicate Mango ").delete()



class Command(BaseCommand):
    help = 'Crear productos con imagen desde comando'

    def handle(self, *args, **kwargs):
        try:
            sucursal = Sucursal.objects.get(id_sucursal=3)  # Cambié id por id_sucursal
        except Sucursal.DoesNotExist:
            self.stdout.write(self.style.ERROR('Sucursal con id_sucursal=3 no existe'))
            return
        
        producto_data = {
            "nombre_producto": "Alicate Mango ",
            "descripcion": "Es un Alicate",
            "marca": "Ferremax",
            "precio_unitario": 5000,
            "stock_total": 200,
            "imagen_path": "media/productos/alicatemango.jpg",
        }

        producto = Producto(
            nombre_producto=producto_data["nombre_producto"],
            descripcion=producto_data["descripcion"],
            marca=producto_data["marca"],
            precio_unitario=producto_data["precio_unitario"],
            stock_total=producto_data["stock_total"],
            sucursal=sucursal,
        )

        imagen_path = producto_data["imagen_path"]
        if os.path.exists(imagen_path):
            with open(imagen_path, "rb") as img_file:
                producto.imagen.save(os.path.basename(imagen_path), File(img_file), save=False)
        else:
            self.stdout.write(self.style.WARNING(f'Imagen no encontrada: {imagen_path}'))

        producto.save()
        self.stdout.write(self.style.SUCCESS(f'Producto "{producto.nombre_producto}" creado exitosamente'))
