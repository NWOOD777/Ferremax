from django.db import migrations

def cargar_empleados(apps, schema_editor):
    Cargo = apps.get_model('appFerremax', 'Cargo')
    Sucursal = apps.get_model('appFerremax', 'Sucursal')
    Empleado = apps.get_model('appFerremax', 'Empleado')

    cargos_objs = {cargo.nombre_cargo: cargo for cargo in Cargo.objects.all()}
    sucursal_objs = list(Sucursal.objects.all())

    empleados = [
        # Sucursal Central
        {"nombre": "Pedro", "apellido": "Bodeguero", "correo": "pedro.bodeguero@gmail.com", "contrasena": "bodeguero123", "cargo": cargos_objs["Bodeguero"], "sucursal": sucursal_objs[0]},
        {"nombre": "Claudia", "apellido": "Contador", "correo": "claudia.contador@gmail.com", "contrasena": "contador123", "cargo": cargos_objs["Contador"], "sucursal": sucursal_objs[0]},
        {"nombre": "Sofía", "apellido": "Vendedor", "correo": "sofia.vendedor@gmail.com", "contrasena": "vendedor123", "cargo": cargos_objs["Vendedor"], "sucursal": sucursal_objs[0]},
        # Sucursal Norte
        {"nombre": "Mario", "apellido": "Bodeguero", "correo": "mario.bodeguero@gmail.com", "contrasena": "bodeguero123", "cargo": cargos_objs["Bodeguero"], "sucursal": sucursal_objs[1]},
        {"nombre": "Patricia", "apellido": "Contador", "correo": "patricia.contador@gmail.com", "contrasena": "contador123", "cargo": cargos_objs["Contador"], "sucursal": sucursal_objs[1]},
        {"nombre": "Diego", "apellido": "Vendedor", "correo": "diego.vendedor@gmail.com", "contrasena": "vendedor123", "cargo": cargos_objs["Vendedor"], "sucursal": sucursal_objs[1]},
        # Sucursal Sur
        {"nombre": "Lucía", "apellido": "Bodeguero", "correo": "lucia.bodeguero@gmail.com", "contrasena": "bodeguero123", "cargo": cargos_objs["Bodeguero"], "sucursal": sucursal_objs[2]},
        {"nombre": "Javier", "apellido": "Contador", "correo": "javier.contador@gmail.com", "contrasena": "contador123", "cargo": cargos_objs["Contador"], "sucursal": sucursal_objs[2]},
        {"nombre": "Valentina", "apellido": "Vendedor", "correo": "valentina.vendedor@gmail.com", "contrasena": "vendedor123", "cargo": cargos_objs["Vendedor"], "sucursal": sucursal_objs[2]},
    ]
    for e in empleados:
        Empleado.objects.get_or_create(
            nombre_empleado=e["nombre"],
            apellido_empleado=e["apellido"],
            correo=e["correo"],
            contrasena=e["contrasena"],
            cargo=e["cargo"],
            sucursal=e["sucursal"]
        )

class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0005_merge_20250531_1847'),
    ]
    operations = [
        migrations.RunPython(cargar_empleados),
    ]
