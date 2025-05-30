from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('inicio/', inicio, name='inicio'),
    path('pedidos/', pedidos, name='pedidos'),
    path('pagos/', pagos, name='pagos'),
]