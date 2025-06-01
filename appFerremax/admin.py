from django.contrib import admin
from .models import (
    Comuna, Sucursal, Cargo, Empleado, Cliente, Producto,
    Pedido, DetalleProducto, Envio, MetodoPago, EstadoPago, Pago
)


# Register your models here.
admin.site.register(Comuna)
admin.site.register(Sucursal)
admin.site.register(Cargo)
admin.site.register(Empleado)
admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(DetalleProducto)
admin.site.register(Envio)
admin.site.register(MetodoPago)
admin.site.register(EstadoPago)
admin.site.register(Pago)