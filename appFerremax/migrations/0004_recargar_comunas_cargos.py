from django.db import migrations

def recargar_comunas_y_cargos(apps, schema_editor):
    Comuna = apps.get_model('appFerremax', 'Comuna')
    Cargo = apps.get_model('appFerremax', 'Cargo')
    Sucursal = apps.get_model('appFerremax', 'Sucursal')
    Empleado = apps.get_model('appFerremax', 'Empleado')
    Cliente = apps.get_model('appFerremax', 'Cliente')

    comunas = [
        "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida",
        "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa",
        "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaquín",
        "San Miguel", "San Ramón", "Santiago", "Vitacura"
    ]
    cargos = [
        "Bodeguero", "Contador", "Vendedor"
    ]

    for nombre in comunas:
        Comuna.objects.get_or_create(nombre_comuna=nombre)
    for nombre in cargos:
        Cargo.objects.get_or_create(nombre_cargo=nombre)

    sucursales = [
        {"nombre": "Sucursal Central", "direccion": "Av. Principal 123", "comuna": "Santiago"},
        {"nombre": "Sucursal Norte", "direccion": "Calle Norte 456", "comuna": "Huechuraba"},
        {"nombre": "Sucursal Sur", "direccion": "Camino Sur 789", "comuna": "La Florida"},
    ]
    sucursal_objs = []
    for s in sucursales:
        comuna_obj, _ = Comuna.objects.get_or_create(nombre_comuna=s["comuna"])
        sucursal_obj, _ = Sucursal.objects.get_or_create(
            nombre_sucursal=s["nombre"],
            direccion=s["direccion"],
            comuna=comuna_obj
        )
        sucursal_objs.append(sucursal_obj)


class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0002_auto_cargar_datos'),
    ]
    operations = [
        migrations.RunPython(recargar_comunas_y_cargos),
    ]
