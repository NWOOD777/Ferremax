from django.db import migrations
from datetime import date

def crear_cliente_por_defecto(apps, schema_editor):
    from django.contrib.auth.hashers import make_password  # Import local para migración

    Cliente = apps.get_model('appFerremax', 'Cliente')
    Comuna = apps.get_model('appFerremax', 'Comuna')
    
    # Verificar si ya existen clientes
    if Cliente.objects.exists():
        return
    
    try:
        # Buscar una comuna para la dirección (opcional, para enriquecer los datos)
        comuna = None
        try:
            comuna = Comuna.objects.filter(nombre_comuna='Santiago').first() or Comuna.objects.first()
        except:
            pass
        
        # Crear un cliente por defecto
        cliente = Cliente.objects.create(
            rut_cliente="11111111-1",
            fecha_registro=date.today(),
            recibe_ofertas="S",
            nombre_cliente="Cliente",
            apellido_cliente="Demo",
            direccion=f"Av. Principal 123 {', ' + comuna.nombre_comuna if comuna else ''}",
            telefono_cliente="912345678",
            correo="alcainodiego0@gmail.com",
            contrasena=make_password("diego123456789")  # Aquí hacemos el hash
        )
        
        print(f"Se ha creado un cliente por defecto con RUT: {cliente.rut_cliente}")
    
    except Exception as e:
        print(f"Error al crear el cliente por defecto: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0012_crear_producto_por_defecto'),
    ]
    
    operations = [
        migrations.RunPython(crear_cliente_por_defecto),
    ]
