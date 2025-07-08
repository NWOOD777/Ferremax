from django.urls import path, include
from rest_framework.routers import DefaultRouter
from appFerremax.viewsets import VendedorViewSet

router = DefaultRouter()
router.register(r'vendedores', VendedorViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
