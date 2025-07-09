from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Crea un superusuario predefinido si no existe'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@ferremax.cl'
        password = 'ferremax2025'
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente'))
            else:
                self.stdout.write(self.style.WARNING(f'El superusuario "{username}" ya existe'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR('Error al crear el superusuario, verifique que el nombre de usuario o email no estén siendo usados'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
