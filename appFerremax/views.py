from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


from appFerremax.forms import ProductoForm
from .models import Cargo, Cliente, Empleado, Sucursal, Producto, Pedido, DetalleProducto, MetodoPago, EstadoPago, Pago
from .paypal_utils import crear_pago, ejecutar_pago
from decimal import Decimal
import json
from datetime import date

# Create your views here.
def index(request):
    nombre_usuario = request.session.get('nombre_usuario')
    productos = Producto.objects.all()
    return render(request, 'Home/index.html', {'nombre_usuario': nombre_usuario, 'productos': productos})




from django.shortcuts import render, redirect
from .models import Cliente, Empleado

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
                empleado = Empleado.objects.get(correo=correo)
                if hasattr(empleado, 'contrasena') and contrasena == empleado.contrasena:
                    request.session['nombre_usuario'] = f"{empleado.nombre_empleado} {empleado.apellido_empleado}"
                    request.session['tipo_usuario'] = empleado.cargo.nombre_cargo
                    return redirect('index')
                else:
                    errors.append('Contraseña incorrecta.')
            except Empleado.DoesNotExist:
                try:
                    cliente = Cliente.objects.get(correo=correo)
                    if hasattr(cliente, 'contrasena') and contrasena == cliente.contrasena:
                        request.session['nombre_usuario'] = cliente.nombre_cliente
                        request.session['tipo_usuario'] = 'cliente'
                        return redirect('index')
                    else:
                        errors.append('Contraseña incorrecta.')
                except Cliente.DoesNotExist:
                    errors.append('Correo no registrado.')
        return render(request, 'Home/inicio.html', {'errores': errors, 'valores': valores})
    return render(request, 'Home/inicio.html')

def pedidos(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    tipo_usuario = request.session.get('tipo_usuario')
    
    if tipo_usuario == 'cliente':
        try:
            nombre_cliente = request.session.get('nombre_usuario')
            cliente = Cliente.objects.get(nombre_cliente=nombre_cliente)
            
            pedidos_cliente = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
            
            return render(request, 'Home/pedidos.html', {
                'pedidos': pedidos_cliente
            })
        except Cliente.DoesNotExist:
            return redirect('index')
    else:
        if tipo_usuario == 'Vendedor' or tipo_usuario == 'Administrador':
            pedidos_todos = Pedido.objects.all().order_by('-fecha_pedido')
            return render(request, 'Home/pedidos.html', {
                'pedidos': pedidos_todos
            })
    
    return render(request, 'Home/pedidos.html')

def pagos(request):
    
    return render(request, 'Home/pagos.html')

def bodeguero(request):
    # Verificar que el usuario esté autenticado y sea bodeguero
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
        
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario != 'Bodeguero':
        return redirect('index')
        
    # Obtener los pedidos que no están completados aún
    pedidos = Pedido.objects.filter(estado_pedido__in=['Pendiente', 'Aprobado', 'Preparado'])
    
    # Cargar los detalles de cada pedido
    for pedido in pedidos:
        pedido.detalles = DetalleProducto.objects.filter(pedido=pedido)
        
    return render(request, 'Home/bodeguero.html', {'pedidos': pedidos})

@csrf_exempt
def cambiar_estado_pedido(request, id_pedido):
    # Verificar que el usuario esté autenticado y sea bodeguero
    if 'nombre_usuario' not in request.session:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        return redirect('inicio')
        
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario != 'Bodeguero':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        return redirect('index')
    
    if request.method == 'POST':
        # Determinar si es una solicitud AJAX o normal
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        # Obtener el nuevo estado del pedido
        if is_ajax:
            try:
                data = json.loads(request.body)
                nuevo_estado = data.get('nuevo_estado')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        else:
            nuevo_estado = request.POST.get('nuevo_estado')
        
        # Validar que el nuevo estado sea válido
        ESTADOS_VALIDOS = ['Pendiente', 'Aprobado', 'Preparado', 'Enviado', 'Entregado']
        if nuevo_estado not in ESTADOS_VALIDOS:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
            messages.error(request, 'Estado no válido')
            return redirect('bodeguero')
        
        try:
            pedido = Pedido.objects.get(id_pedido=id_pedido)
            pedido.estado_pedido = nuevo_estado
            pedido.save()
            
            if is_ajax:
                return JsonResponse({'success': True, 'estado': nuevo_estado})
            
            messages.success(request, f'El pedido #{id_pedido} ha sido actualizado a {nuevo_estado}')
        except Pedido.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'El pedido #{id_pedido} no existe'}, status=404)
            messages.error(request, f'El pedido #{id_pedido} no existe')
            
    return redirect('bodeguero')

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
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.method == 'POST':
        cart_data = json.loads(request.body)
        request.session['carrito'] = cart_data
        return JsonResponse({'status': 'success'})
    
    productos = Producto.objects.all()
    carrito = request.session.get('carrito', [])
    
    return render(request, 'Home/carrito.html', {
        'productos': productos,
        'carrito': carrito
    })

def checkout(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session.get('tipo_usuario') != 'cliente':
        return redirect('index')
    
    carrito = request.session.get('carrito', [])
    if not carrito:
        return redirect('carrito')
    
    total = Decimal('0.00')
    items = []
    
    for item in carrito:
        producto = Producto.objects.get(id_producto=item['id'])
        subtotal = Decimal(str(producto.precio_unitario)) * int(item['cantidad'])
        total += subtotal
        
        items.append({
            "name": producto.nombre_producto,
            "sku": str(producto.id_producto),
            "price": str(producto.precio_unitario),
            "currency": "USD",
            "quantity": item['cantidad']
        })
    
    base_url = request.build_absolute_uri('/')[:-1]
    redirect_urls = {
        "return_url": f"{base_url}{reverse('ejecutar_pago')}",
        "cancel_url": f"{base_url}{reverse('carrito')}"
    }
    
    payment = crear_pago(
        items=items, 
        total=total, 
        descripcion="Compra en Ferremax", 
        redirect_urls=redirect_urls
    )
    
    if payment:
        request.session['paypal_payment_id'] = payment.id
        request.session['paypal_total'] = str(total)
        
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    
    return redirect('carrito')

@csrf_exempt
def ejecutar_pago_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            payment_id = data.get('payment_id')
            payer_id = data.get('payer_id')

            # Busca el cliente en sesión
            nombre_usuario = request.session.get('nombre_usuario')
            if not nombre_usuario:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})

            cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
            if not cliente:
                return JsonResponse({'success': False, 'error': 'Cliente no encontrado'})

            # Calcula el total
            total = sum(float(item['price']) * int(item['quantity']) for item in cart)

            # Verificar carrito vacío
            if not cart:
                return JsonResponse({'success': False, 'error': 'El carrito está vacío'})

            # Verificar stock de productos
            for item in cart:
                try:
                    producto = Producto.objects.get(id_producto=item['id'])
                    if producto.stock_total < int(item['quantity']):
                        return JsonResponse({'success': False, 'error': f'No hay suficiente stock para {producto.nombre_producto}'})
                except Producto.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Producto no encontrado'})

            # Verificar total mayor a cero
            if total <= 0:
                return JsonResponse({'success': False, 'error': 'El total debe ser mayor a cero'})

            # Crea el pedido
            pedido = Pedido.objects.create(
                fecha_pedido=date.today(),
                estado_pedido="Aprobado",
                tipo_entrega="Despacho",
                cliente=cliente,
                paypal_payment_id=payment_id,
                total=total
            )

            # Crea los detalles y actualiza stock
            for item in cart:
                producto = Producto.objects.get(id_producto=item['id'])
                DetalleProducto.objects.create(
                    cantidad=item['quantity'],
                    producto=producto,
                    pedido=pedido
                )
                producto.stock_total -= int(item['quantity'])
                producto.save()

            # Crea el registro de pago en la tabla Pago
            metodo_pago = MetodoPago.objects.get(nombre_metodo_pago="PayPal")
            estado_pago = EstadoPago.objects.get(estado_pago="Completado")
            Pago.objects.create(
                fecha=date.today(),
                pedido=pedido,
                metodo_pago=metodo_pago,
                estado_pago=estado_pago
            )

            # Limpia el carrito en sesión si existe
            if 'carrito' in request.session:
                del request.session['carrito']

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error al procesar el pedido: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def cerrar_sesion(request):
    request.session.flush()  
    return redirect('index') 

from django.shortcuts import render, redirect
from .forms import ProductoForm
from .models import Producto

def crearproductos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            
            if 'nombre_usuario' in request.session and 'tipo_usuario' in request.session:
                if request.session['tipo_usuario'] != 'cliente':
                    nombre_completo = request.session['nombre_usuario']
                    nombres = nombre_completo.split(' ', 1)
                    nombre = nombres[0]
                    apellido = nombres[1] if len(nombres) > 1 else ''
                    
                    try:
                        empleado = Empleado.objects.get(
                            nombre_empleado=nombre,
                            apellido_empleado=apellido
                        )
                        producto.creado_por = empleado
                    except Empleado.DoesNotExist:
                        pass
            
            producto.save()
            return render(request, 'Home/crearproductos.html', {
                'form': ProductoForm(),
                'mensaje': 'Producto creado exitosamente'
            })
    else:
        form = ProductoForm()
    
    return render(request, 'Home/crearproductos.html', {'form': form})

def mis_productos(request):
    if 'nombre_usuario' not in request.session or 'tipo_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session['tipo_usuario'] == 'cliente':
        return redirect('index')
    
    nombre_completo = request.session['nombre_usuario']
    nombres = nombre_completo.split(' ', 1)
    nombre = nombres[0]
    apellido = nombres[1] if len(nombres) > 1 else ''
    
    try:
        empleado = Empleado.objects.get(
            nombre_empleado=nombre,
            apellido_empleado=apellido
        )
        
        productos = Producto.objects.filter(creado_por=empleado).order_by('-fecha_creacion')
        
        return render(request, 'Home/mis_productos.html', {
            'productos': productos,
            'empleado': empleado
        })
    except Empleado.DoesNotExist:
        return redirect('index')

def modificar_producto(request, id_producto):
    try:
        producto = Producto.objects.get(id_producto=id_producto)
        
        if 'nombre_usuario' not in request.session or 'tipo_usuario' not in request.session:
            return redirect('inicio')
        
        if request.session['tipo_usuario'] == 'cliente':
            return redirect('index')
        
        nombre_completo = request.session['nombre_usuario']
        nombres = nombre_completo.split(' ', 1)
        nombre = nombres[0]
        apellido = nombres[1] if len(nombres) > 1 else ''
        
        try:
            empleado = Empleado.objects.get(
                nombre_empleado=nombre,
                apellido_empleado=apellido
            )
            
            if producto.creado_por != empleado:
                return redirect('mis_productos')
            
        except Empleado.DoesNotExist:
            return redirect('index')
        
        if request.method == 'POST':
            form = ProductoForm(request.POST, request.FILES, instance=producto)
            if form.is_valid():
                form.save()
                return render(request, 'Home/modificar_producto.html', {
                    'form': form, 
                    'producto': producto,
                    'mensaje': 'Producto actualizado exitosamente',
                    'actualizado': True
                })
        else:
            form = ProductoForm(instance=producto)
        return render(request, 'Home/modificar_producto.html', {
            'form': form,
            'producto': producto
        })
    except Producto.DoesNotExist:
        return redirect('mis_productos')

def eliminar_producto(request, id_producto):
    try:
        producto = Producto.objects.get(id_producto=id_producto)
        
        if 'nombre_usuario' not in request.session or 'tipo_usuario' not in request.session:
            return redirect('inicio')
        
        if request.session['tipo_usuario'] == 'cliente':
            return redirect('index')
        
        nombre_completo = request.session['nombre_usuario']
        nombres = nombre_completo.split(' ', 1)
        nombre = nombres[0]
        apellido = nombres[1] if len(nombres) > 1 else ''
        
        try:
            empleado = Empleado.objects.get(
                nombre_empleado=nombre,
                apellido_empleado=apellido
            )
            
            if producto.creado_por != empleado:
                return redirect('mis_productos')
            
            producto.delete()
            
            from django.contrib import messages
            messages.success(request, f'El producto "{producto.nombre_producto}" ha sido eliminado correctamente.')
            
        except Empleado.DoesNotExist:
            return redirect('index')
        
        return redirect('mis_productos')
        
    except Producto.DoesNotExist:
        return redirect('mis_productos')

def recuperar_contrasena(request):
    
    errors = []
    mensaje = ''
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        if not correo:
            errors.append('Debe ingresar su correo electrónico.')
        else:
            # Buscar en Cliente y Empleado
            user = None
            try:
                user = Cliente.objects.get(correo=correo)
                user_type = 'cliente'
            except Cliente.DoesNotExist:
                try:
                    user = Empleado.objects.get(correo=correo)
                    user_type = 'empleado'
                except Empleado.DoesNotExist:
                    errors.append('El correo no está registrado.')
            if user and not errors:
                # Generar token simple (en producción usar PasswordResetTokenGenerator)
                token = get_random_string(32)
                # Guardar el token en sesión (o en la base de datos si lo deseas)
                request.session['reset_token'] = token
                request.session['reset_email'] = correo
                # Construir enlace de recuperación
                reset_url = request.build_absolute_uri(
                    reverse('resetear_contrasena') + f'?token={token}'
                )
                # Renderizar email
                subject = 'Recupera tu contraseña - Ferremax'
                message = render_to_string('Home/email_recuperar_contrasena.txt', {
                    'reset_url': reset_url,
                    'nombre': getattr(user, 'nombre_cliente', getattr(user, 'nombre_empleado', 'Usuario')),
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [correo])
                mensaje = 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.'
    return render(request, 'Home/recuperar_contrasena.html', {'errores': errors, 'mensaje': mensaje})


