from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from appFerremax import views

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
    path('cambiar_estado_pedido/<int:id_pedido>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
        #recuperar
    #path('recuperar_contrasena/', recuperar_contrasena, name='recuperar_contrasena'),
    path('recuperar_contrasena/', auth_views.PasswordResetView.as_view(template_name="Home/recuperar_contra/recuperar_contrasena.html"), name="recuperar_contrasena"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="Home/recuperar_contra/contra_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="Home/recuperar_contra/contra_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="Home/recuperar_contra/contra_reset_done.html"), name="password_reset_complete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)