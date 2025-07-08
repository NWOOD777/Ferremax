from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .api_urls import urlpatterns as api_urlpatterns
from .views import ProductoListCreate, ProductoRetrieveUpdateDestroy

urlpatterns = [
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pagos/', views.pagos, name='pagos'),
    path('bodeguero/', views.bodeguero, name='bodeguero'),
    path('registro/', views.registro, name='registro'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar_al_carrito/<int:id_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('remove_from_cart/<int:id_producto>/', views.remove_from_cart, name='remove_from_cart'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    #path('crearproductos/', views.crearproductos, name='crearproductos'),
    #path('mis_productos/', views.mis_productos, name='mis_productos'),
    #path('modificar_producto/<int:id_producto>/', views.modificar_producto, name='modificar_producto'),
    #path('eliminar_producto/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('checkout/', views.checkout, name='checkout'),
    path('ejecutar_pago/', views.ejecutar_pago_view, name='ejecutar_pago'),
    path('cambiar_estado_pedido/<int:id_pedido>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('recuperar_contrasena/', auth_views.PasswordResetView.as_view(template_name="Home/recuperar_contra/recuperar_contrasena.html"), name="recuperar_contrasena"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="Home/recuperar_contra/contra_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="Home/recuperar_contra/contra_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="Home/recuperar_contra/contra_reset_done.html"), name="password_reset_complete"),
    path('check_stock/', views.check_stock, name='check_stock'),
    path('api_dolar/', views.api_dolar, name='api_dolar'),
    path('api-dolar-json/', views.api_dolar_json, name='api_dolar_json'),
    # API productos
    path('productos/', ProductoListCreate.as_view(), name='producto-list'),
    path('productos/<int:pk>/', ProductoRetrieveUpdateDestroy.as_view(), name='producto-detail'),
] + api_urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
