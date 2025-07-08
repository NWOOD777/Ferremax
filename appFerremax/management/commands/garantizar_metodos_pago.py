from django.core.management.base import BaseCommand
from appFerremax.models import MetodoPago, EstadoPago

class Command(BaseCommand):
    help = 'Asegura que los métodos de pago y estados básicos existan en la base de datos local'

    def handle(self, *args, **options):
        # ID y nombres de los métodos de pago (basados en la captura de pantalla de Oracle)
        metodos_pago = [
            (1, "PayPal"),
            (2, "Tarjeta de Crédito"),
            (3, "Transferencia")
        ]
        
        for id_metodo, nombre in metodos_pago:
            try:
                # Intentar obtener por ID
                metodo = MetodoPago.objects.filter(id_metodo_pago=id_metodo).first()
                if metodo:
                    # Actualizar nombre si es necesario
                    if metodo.nombre_metodo_pago != nombre:
                        metodo.nombre_metodo_pago = nombre
                        metodo.save()
                        self.stdout.write(self.style.SUCCESS(f"Método de pago actualizado: ID={id_metodo}, Nombre={nombre}"))
                    else:
                        self.stdout.write(f"Método de pago existente: ID={id_metodo}, Nombre={nombre}")
                else:
                    # Crear nuevo con ID específico
                    MetodoPago.objects.create(id_metodo_pago=id_metodo, nombre_metodo_pago=nombre)
                    self.stdout.write(self.style.SUCCESS(f"Método de pago creado: ID={id_metodo}, Nombre={nombre}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar método de pago ID={id_metodo}: {str(e)}"))
                
        # Estados de pago
        estados_pago = [
            (1, "Completado"),
            (2, "Pendiente"),
            (3, "Rechazado"),
            (4, "Reembolsado")
        ]
        
        for id_estado, nombre in estados_pago:
            try:
                # Intentar obtener por ID
                estado = EstadoPago.objects.filter(id_estado_pago=id_estado).first()
                if estado:
                    # Actualizar nombre si es necesario
                    if estado.estado_pago != nombre:
                        estado.estado_pago = nombre
                        estado.save()
                        self.stdout.write(self.style.SUCCESS(f"Estado de pago actualizado: ID={id_estado}, Nombre={nombre}"))
                    else:
                        self.stdout.write(f"Estado de pago existente: ID={id_estado}, Nombre={nombre}")
                else:
                    # Crear nuevo con ID específico
                    EstadoPago.objects.create(id_estado_pago=id_estado, estado_pago=nombre)
                    self.stdout.write(self.style.SUCCESS(f"Estado de pago creado: ID={id_estado}, Nombre={nombre}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar estado de pago ID={id_estado}: {str(e)}"))
                
        # Mostrar resumen
        metodos = MetodoPago.objects.all()
        estados = EstadoPago.objects.all()
        self.stdout.write(f"\nResumen: {metodos.count()} métodos de pago y {estados.count()} estados de pago disponibles.")
