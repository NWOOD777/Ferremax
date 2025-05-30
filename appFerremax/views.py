from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'Home/index.html')

def inicio(request):
    return render(request, 'Home/inicio.html')

def pedidos(request):
    return render(request, 'Home/pedidos.html')

def pagos(request):
    return render(request, 'Home/pagos.html')