from django.core.management.base import BaseCommand
from appFerremax.models import MetodoPago
from django.conf import settings
import sys
import os

class Command(BaseCommand):
    help = 'Verifica y muestra los métodos de pago disponibles'

    def handle(self, *args, **options):
        # Verificar configuración de la base de datos
        self.stdout.write("Configuración de base de datos actual:")
        db_config = settings.DATABASES['default']
        self.stdout.write(f"  - Engine: {db_config['ENGINE']}")
        self.stdout.write(f"  - Name: {db_config['NAME']}")
        self.stdout.write(f"  - User: {db_config['USER']}")
        self.stdout.write(f"  - Host: {db_config['HOST']}")
        self.stdout.write(f"  - Port: {db_config['PORT']}")
        
        # Verificar si cx_Oracle está disponible
        self.stdout.write("\nVerificando cx_Oracle:")
        try:
            import cx_Oracle
            self.stdout.write(self.style.SUCCESS(f"  - cx_Oracle instalado correctamente (versión {cx_Oracle.version})"))
        except ImportError:
            self.stdout.write(self.style.ERROR("  - cx_Oracle no está instalado"))
            self.stdout.write("  - Para instalar: pip install cx_Oracle")
        
        # Verificar ORACLE_HOME y PATH para el cliente Oracle
        self.stdout.write("\nVerificando variables de entorno de Oracle:")
        oracle_home = os.environ.get('ORACLE_HOME', 'No definido')
        oracle_path = os.environ.get('PATH', '')
        self.stdout.write(f"  - ORACLE_HOME: {oracle_home}")
        
        try:
            # Intentar conectar directamente con Oracle si cx_Oracle está disponible
            self.stdout.write("\nIntentando conexión directa con Oracle...")
            import cx_Oracle
            try:
                connection = cx_Oracle.connect(
                    db_config['USER'],
                    db_config['PASSWORD'],
                    f"{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
                )
                self.stdout.write(self.style.SUCCESS("  - Conexión directa con Oracle exitosa!"))
                cursor = connection.cursor()
                cursor.execute("SELECT ID_METODO_PAGO, NOMBRE_METODO_PAGO FROM APPFERRREMAX_METODOPAGO")
                self.stdout.write("  - Métodos de pago desde Oracle (consulta directa):")
                for row in cursor:
                    self.stdout.write(f"    * ID: {row[0]}, Nombre: {row[1]}")
                cursor.close()
                connection.close()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error en conexión directa con Oracle: {str(e)}"))
        except ImportError:
            pass
        
        # Verificar con Django ORM
        self.stdout.write("\nVerificando métodos de pago con Django ORM:")
        try:
            metodos = MetodoPago.objects.all()
            count = metodos.count()
            
            self.stdout.write(self.style.SUCCESS(f"Se encontraron {count} métodos de pago:"))
            
            for metodo in metodos:
                self.stdout.write(f"  - ID: {metodo.id_metodo_pago}, Nombre: '{metodo.nombre_metodo_pago}'")
            
            # Si no hay métodos, intentar crear uno para PayPal
            if count == 0:
                self.stdout.write(self.style.WARNING("No se encontraron métodos de pago. Creando método PayPal..."))
                try:
                    metodo = MetodoPago.objects.create(nombre_metodo_pago="PayPal")
                    self.stdout.write(self.style.SUCCESS(f"Método de pago creado: {metodo.id_metodo_pago} - {metodo.nombre_metodo_pago}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error al crear método de pago: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al consultar con Django ORM: {str(e)}"))
