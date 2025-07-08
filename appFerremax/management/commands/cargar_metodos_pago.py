from django.core.management.base import BaseCommand
from appFerremax.models import MetodoPago, EstadoPago

class Command(BaseCommand):
    help = 'Carga los métodos de pago y estados de pago básicos en la base de datos'

    def handle(self, *args, **options):
        # Métodos de pago
        metodos_pago = [
            "PayPal",
            "Tarjeta de crédito",
            "Tarjeta de débito",
            "Transferencia bancaria"
        ]
        
        for metodo in metodos_pago:
            MetodoPago.objects.get_or_create(nombre_metodo_pago=metodo)
            self.stdout.write(self.style.SUCCESS(f'Método de pago "{metodo}" creado o ya existente'))
        
        # Estados de pago
        estados_pago = [
            "Completado",
            "Pendiente",
            "Rechazado",
            "Reembolsado"
        ]
        
        for estado in estados_pago:
            EstadoPago.objects.get_or_create(estado_pago=estado)
            self.stdout.write(self.style.SUCCESS(f'Estado de pago "{estado}" creado o ya existente'))
        
        self.stdout.write(self.style.SUCCESS('Métodos de pago y estados de pago cargados correctamente'))