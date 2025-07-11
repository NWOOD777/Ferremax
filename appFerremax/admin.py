from django.contrib import admin
from django import forms
from .models import (
    Comuna, Sucursal, Cargo, Empleado, Cliente, Producto,
    Pedido, DetalleProducto, Envio, MetodoPago, EstadoPago, Pago
)


class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter creado_por field to only show Vendedores
        vendedor_cargo = Cargo.objects.filter(nombre_cargo='Vendedor').first()
        if vendedor_cargo:
            self.fields['creado_por'].queryset = Empleado.objects.filter(cargo=vendedor_cargo)
        else:
            self.fields['creado_por'].queryset = Empleado.objects.none()


class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
    list_display = ('nombre_producto', 'marca', 'precio_unitario', 'stock_total', 'creado_por')
    search_fields = ('nombre_producto', 'marca', 'descripcion')
    list_filter = ('sucursal', 'marca')


# Register your models here.
admin.site.register(Comuna)
admin.site.register(Sucursal)
admin.site.register(Cargo)
admin.site.register(Empleado)
admin.site.register(Cliente)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido)
admin.site.register(DetalleProducto)
admin.site.register(Envio)
admin.site.register(MetodoPago)
admin.site.register(EstadoPago)
admin.site.register(Pago)