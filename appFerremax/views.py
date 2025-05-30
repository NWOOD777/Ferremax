from django.shortcuts import render
from django.http import HttpResponse
from .models import Cargo

# Create your views here.
def index(request):
    return render(request, 'Home/index.html')

def inicio(request):
    return render(request, 'Home/inicio.html')

def pedidos(request):
    return render(request, 'Home/pedidos.html')

def pagos(request):
    return render(request, 'Home/pagos.html')

def bodeguero(request):
    return render(request, 'Home/bodeguero.html')

def mostrar_cargo(request):
    cargo = Cargo.objects.all()
    cargos_list = ', '.join([str(c) for c in cargo])
    return HttpResponse(f"Cargo creado: {cargos_list}")