from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Cargo, Cliente

# Create your views here.
def index(request):
    nombre_cliente = request.session.get('cliente_nombre')
    return render(request, 'Home/index.html', {'nombre_cliente': nombre_cliente})




def inicio(request):
    errors = []
    valores = {}
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        valores = {'correo': correo}
        if not correo or not contrasena:
            errors.append('Debe ingresar correo y contraseña.')
        else:
            try:
                cliente = Cliente.objects.get(correo=correo)
                # Validar con el campo contraseña real (debes agregarlo en el modelo Cliente si no existe)
                if hasattr(cliente, 'contrasena') and contrasena == cliente.contrasena:
                    request.session['cliente_nombre'] = cliente.nombre_cliente
                    request.session['cliente_id'] = cliente.rut_cliente
                    return redirect('index')
                else:
                    errors.append('Contraseña incorrecta.')
            except Cliente.DoesNotExist:
                errors.append('Correo no registrado.')
        return render(request, 'Home/inicio.html', {'errores': errors, 'valores': valores})
    return render(request, 'Home/inicio.html')

def pedidos(request):
    return render(request, 'Home/pedidos.html')

def pagos(request):
    return render(request, 'Home/pagos.html')

def bodeguero(request):
    return render(request, 'Home/bodeguero.html')

def registro(request):
    from django.core.exceptions import ValidationError
    import re
    errors = []
    valores = {}
    if request.method == 'POST':
        rut = request.POST.get('rut_cliente', '').strip()
        nombre = request.POST.get('nombre_cliente', '').strip()
        apellido = request.POST.get('apellido_cliente', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono_cliente', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        recibe_ofertas = request.POST.get('recibe_ofertas', '').strip().upper()
        fecha_registro = request.POST.get('fecha_registro', '')

        valores = {
            'rut_cliente': rut,
            'nombre_cliente': nombre,
            'apellido_cliente': apellido,
            'direccion': direccion,
            'telefono_cliente': telefono,
            'correo': correo,
            'recibe_ofertas': recibe_ofertas,
            'fecha_registro': fecha_registro,
        }
        rut_pattern = r"^\d{7,8}-[\dkK]$"
        if not rut or not re.match(rut_pattern, rut):
            errors.append('El RUT es obligatorio y debe tener formato 12345678-9.')
        if not nombre:
            errors.append('El nombre es obligatorio.')
        if not apellido:
            errors.append('El apellido es obligatorio.')
        if not direccion:
            errors.append('La dirección es obligatoria.')
        if not telefono or len(telefono) < 8 or not telefono.isdigit():
            errors.append('El teléfono debe tener al menos 8 dígitos y solo números.')
        if not correo:
            errors.append('El correo es obligatorio.')
        elif Cliente.objects.filter(correo=correo).exists():
            errors.append('El correo ya está registrado.')
        if not contrasena or len(contrasena) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres.')
        if recibe_ofertas not in ['S', 'N']:
            errors.append('Debe seleccionar si recibe ofertas (Sí o No).')
        if not fecha_registro:
            errors.append('La fecha de registro es obligatoria.')

        if errors:
            return render(request, 'Home/registro.html', {'errores': errors, 'valores': valores})

        try:
            Cliente.objects.create(
                rut_cliente=rut,
                fecha_registro=fecha_registro,
                recibe_ofertas=recibe_ofertas,
                nombre_cliente=nombre,
                apellido_cliente=apellido,
                direccion=direccion,
                telefono_cliente=telefono,
                correo=correo,
                contrasena=contrasena
            )
            return redirect('inicio')
        except ValidationError as e:
            errors.extend(e.messages)
            return render(request, 'Home/registro.html', {'errores': errors, 'valores': valores})

    from datetime import date
    valores['fecha_registro'] = date.today().isoformat()
    return render(request, 'Home/registro.html', {'valores': valores})

def carrito(request):
    return render(request, 'Home/carrito.html')

