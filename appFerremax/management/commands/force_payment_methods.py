from django.core.management.base import BaseCommand
from appFerremax.models import MetodoPago

class Command(BaseCommand):
    help = 'Fuerza la creación de métodos de pago en la base de datos actual'

    def handle(self, *args, **options):
        self.stdout.write("Creando métodos de pago en la base de datos actual...")
        
        metodos_pago = [
            {"id": 1, "nombre": "PayPal"},
            {"id": 2, "nombre": "Tarjeta de Crédito"},
            {"id": 3, "nombre": "Transferencia"}
        ]
        
        for metodo in metodos_pago:
            try:
                mp, created = MetodoPago.objects.update_or_create(
                    id_metodo_pago=metodo["id"],
                    defaults={"nombre_metodo_pago": metodo["nombre"]}
                )
                status = "creado" if created else "actualizado"
                self.stdout.write(self.style.SUCCESS(f"Método {mp.id_metodo_pago} - '{mp.nombre_metodo_pago}' {status}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al crear método {metodo['nombre']}: {str(e)}"))
