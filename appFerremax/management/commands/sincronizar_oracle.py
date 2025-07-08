from django.core.management.base import BaseCommand
from appFerremax.models import MetodoPago, Pago, Pedido
import cx_Oracle

class Command(BaseCommand):
    help = 'Carga datos desde Oracle para usar en la aplicación local'

    def handle(self, *args, **options):
        self.stdout.write("Cargando datos de Oracle para su uso local...")
        
        try:
            # Configuración de conexión a Oracle
            connection = cx_Oracle.connect(
                user="BDFerremas",
                password="BDFerremas",
                dsn="localhost:1521/orcl"
            )
            self.stdout.write(self.style.SUCCESS("Conexión con Oracle establecida"))
            
            # Obtener los métodos de pago de Oracle
            cursor = connection.cursor()
            cursor.execute("SELECT ID_METODO_PAGO, NOMBRE_METODO_PAGO FROM APPFERRREMAX_METODOPAGO")
            metodos_pago = cursor.fetchall()
            
            # Sincronizar con la tabla local
            self.stdout.write("Sincronizando métodos de pago...")
            for id_metodo, nombre_metodo in metodos_pago:
                # Verificar si ya existe
                metodo, created = MetodoPago.objects.get_or_create(
                    id_metodo_pago=id_metodo,
                    defaults={'nombre_metodo_pago': nombre_metodo}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Creado: {id_metodo} - {nombre_metodo}"))
                else:
                    # Actualizar el nombre si es necesario
                    if metodo.nombre_metodo_pago != nombre_metodo:
                        metodo.nombre_metodo_pago = nombre_metodo
                        metodo.save()
                        self.stdout.write(self.style.SUCCESS(f"Actualizado: {id_metodo} - {nombre_metodo}"))
                    else:
                        self.stdout.write(f"Ya existe: {id_metodo} - {nombre_metodo}")
            
            cursor.close()
            connection.close()
            
            # Verificar la sincronización
            metodos = MetodoPago.objects.all()
            self.stdout.write(f"\nSincronización completada. Métodos disponibles ({metodos.count()}):")
            for metodo in metodos:
                self.stdout.write(f"  - {metodo.id_metodo_pago}: {metodo.nombre_metodo_pago}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante la sincronización: {str(e)}"))
