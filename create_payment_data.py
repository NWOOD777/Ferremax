import os
import django
import random
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PaginaFerremax.settings')
django.setup()

# Importar modelos
from appFerremax.models import MetodoPago, EstadoPago, Pago, Pedido, Cliente, DetalleProducto, Producto

# Crear métodos de pago si no existen
if MetodoPago.objects.count() == 0:
    metodos = ['PayPal', 'Transferencia', 'Tarjeta de Crédito', 'Débito']
    for metodo in metodos:
        MetodoPago.objects.create(nombre_metodo_pago=metodo)
    print("Métodos de pago creados")

# Crear estados de pago si no existen
if EstadoPago.objects.count() == 0:
    estados = ['Aprobado', 'Rechazado', 'Pendiente', 'En proceso']
    for estado in estados:
        EstadoPago.objects.create(estado_pago=estado)
    print("Estados de pago creados")

# Si hay pedidos pero no hay pagos, crear pagos de prueba
if Pedido.objects.count() > 0 and Pago.objects.count() == 0:
    # Obtener pedidos
    pedidos = Pedido.objects.all()
    
    # Obtener métodos y estados
    metodos = list(MetodoPago.objects.all())
    estados = list(EstadoPago.objects.all())
    
    # Crear pagos
    for pedido in pedidos:
        # Seleccionar método y estado aleatorios
        metodo = random.choice(metodos)
        estado = random.choice(estados)
        
        # Fecha de hace 1-10 días
        dias_atras = random.randint(1, 10)
        fecha_pago = date.today() - timedelta(days=dias_atras)
        
        # Crear pago
        Pago.objects.create(
            fecha=fecha_pago,
            pedido=pedido,
            metodo_pago=metodo,
            estado_pago=estado
        )
    
    print(f"Se crearon {len(pedidos)} pagos de prueba")
else:
    print(f"Ya existen pagos o no hay pedidos para asociar: {Pago.objects.count()} pagos, {Pedido.objects.count()} pedidos")

print("Proceso completado")
