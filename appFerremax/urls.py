from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .api_urls import urlpatterns as api_urlpatterns
from appFerremax.forms import ClientePasswordResetForm  # Form personalizado

urlpatterns = [
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pagos/', views.pagos, name='pagos'),
    path('bodeguero/', views.bodeguero, name='bodeguero'),
    path('registro/', views.registro_cliente, name='registro'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar_al_carrito/<int:id_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('remove_from_cart/<int:id_producto>/', views.remove_from_cart, name='remove_from_cart'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('empleados/', views.empleados_direct, name='empleados'),
    path('api_empleados_django/', views.api_empleados_django, name='api_empleados_django'),
    path('checkout/', views.checkout, name='checkout'),
    path('ejecutar_pago/', views.ejecutar_pago_view, name='ejecutar_pago'),
    path('ejecutar_pago_ajax/', views.ejecutar_pago_ajax, name='ejecutar_pago_ajax'),
    path('confirmacion_pedido/<int:id_pedido>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('cambiar_estado_pedido/<int:id_pedido>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

   
    path(
        'recuperar-contrasena/',
        auth_views.PasswordResetView.as_view(
            form_class=ClientePasswordResetForm,  
            template_name='home/recuperar_contra/recuperar_contrasena.html',
            success_url='/recuperar-contrasena/enviado/'
        ),
        name='password_reset'
    ),


    path(
        'recuperar-contrasena/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='home/recuperar_contra/contra_reset_sent.html'
        ),
        name='password_reset_done'
    ),

 
    path(
        'recuperar-contrasena/confirmar/<str:token>/',
        views.cambiar_contrasena_cliente,
        name='cambiar_contrasena_cliente'
    ),



    path('check_stock/', views.check_stock, name='check_stock'),
    path('api_dolar/', views.api_dolar, name='api_dolar'),
    path('api-dolar-json/', views.api_dolar_json, name='api_dolar_json'),
    path('crearproductos/', views.crearproductos, name='crearproductos'),
    path('mis_productos/', views.mis_productos, name='mis_productos'),
    path('modificar_producto/<int:id_producto>/', views.modificar_producto, name='modificar_producto'),
    path('eliminar_producto/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('herramientas/', views.herramientas, name='herramientas'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('productos/', views.productos, name='productos'),
    path('productosapi/', views.productosapi, name='productosapi'),
    path('test-404/', views.test_404, name='test_404'),
]

urlpatterns += api_urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
