from django.db import migrations

def cargar_comunas_y_cargos(apps, schema_editor):
    Comuna = apps.get_model('appFerremax', 'Comuna')
    Cargo = apps.get_model('appFerremax', 'Cargo')

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

class Migration(migrations.Migration):
    dependencies = [
        ('appFerremax', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(cargar_comunas_y_cargos),
    ]
