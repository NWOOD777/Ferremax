from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('inicio/', inicio, name='inicio'),
    path('pedidos/', pedidos, name='pedidos'),
    path('pagos/', pagos, name='pagos'),
    path('bodeguero/', bodeguero, name='bodeguero'),
    path('registro/', registro, name='registro'),
    path('carrito/', carrito, name='carrito'),
    path('cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),
    path('crearproductos/', crearproductos, name='crearproductos'),
    path('mis_productos/', mis_productos, name='mis_productos'),
    path('modificar_producto/<int:id_producto>/', modificar_producto, name='modificar_producto'),
    path('eliminar_producto/<int:id_producto>/', eliminar_producto, name='eliminar_producto'),
    path('checkout/', checkout, name='checkout'),
    path('ejecutar_pago/', ejecutar_pago_view, name='ejecutar_pago'),
    path('recuperar_contrasena/', recuperar_contrasena, name='recuperar_contrasena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)