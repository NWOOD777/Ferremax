from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import json
from decimal import Decimal
from datetime import date

from .models import Cargo, Cliente, Empleado, Sucursal, Producto, Pedido, DetalleProducto, MetodoPago, EstadoPago, Pago
from .paypal_utils import crear_pago, ejecutar_pago

# Create your views here.
def index(request):
    nombre_usuario = request.session.get('nombre_usuario')
    productos = Producto.objects.all()
    
    # Calculate total cart items for display
    carrito = request.session.get('carrito', [])
    total_items = sum(item['cantidad'] for item in carrito) if carrito else 0
    
    return render(request, 'Home/index.html', {
        'nombre_usuario': nombre_usuario,
        'productos': productos,
        'total_items': total_items
    })

def inicio(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        errores = []
        valores = {'correo': correo}
        
        # Validaciones
        if not correo or not contrasena:
            errores.append('Todos los campos son obligatorios')
        
        if not errores:
            # Primero intentamos autenticar como Cliente
            try:
                cliente = Cliente.objects.get(correo=correo)
                if cliente.contrasena == contrasena:
                    # Autenticación exitosa como cliente
                    request.session['nombre_usuario'] = cliente.nombre_cliente
                    request.session['tipo_usuario'] = 'cliente'
                    request.session['id_usuario'] = cliente.rut_cliente  # Usando rut_cliente en lugar de id_cliente
                    return redirect('index')
                else:
                    errores.append('Contraseña incorrecta')
            except Cliente.DoesNotExist:
                # Si no es cliente, intentamos con Empleado
                try:
                    empleado = Empleado.objects.get(correo=correo)
                    if empleado.contrasena == contrasena:
                        # Autenticación exitosa como empleado
                        request.session['nombre_usuario'] = empleado.nombre_empleado
                        request.session['tipo_usuario'] = empleado.cargo.nombre_cargo
                        request.session['id_usuario'] = empleado.id_empleado
                        return redirect('index')
                    else:
                        errores.append('Contraseña incorrecta')
                except Empleado.DoesNotExist:
                    errores.append('El correo no está registrado')
                    
        return render(request, 'Home/inicio.html', {'errores': errores, 'valores': valores})
                
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
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    # Verificar que el usuario sea contador o administrador
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario not in ['Contador', 'Administrador']:
        return redirect('index')
    
    # Obtener nombre de usuario para mostrar en la página
    nombre_usuario = request.session.get('nombre_usuario')
    
    # Obtener todos los pagos realizados
    try:
        pagos = Pago.objects.select_related('pedido', 'metodo_pago', 'estado_pago').all()
    except Exception as e:
        print(f"Error al obtener pagos: {e}")
        pagos = []
    
    # Crear lista de transacciones (usando DetalleProducto)
    try:
        detalles = DetalleProducto.objects.select_related('pedido', 'producto').all()
        transacciones = []
        for detalle in detalles:
            try:
                transaccion = {
                    'id': detalle.id,
                    'fecha': detalle.pedido.fecha_pedido,
                    'cliente': detalle.pedido.cliente.nombre_cliente + ' ' + detalle.pedido.cliente.apellido_cliente,
                    'producto': detalle.producto.nombre_producto,
                    'cantidad': detalle.cantidad,
                    'total': float(detalle.producto.precio_unitario * detalle.cantidad)
                }
                transacciones.append(transaccion)
            except Exception as e:
                print(f"Error procesando detalle {detalle.id}: {e}")
                continue
    except Exception as e:
        print(f"Error al obtener detalles: {e}")
        transacciones = []
    
    # Calcular totales para el balance
    total_ventas = sum(t['total'] for t in transacciones) if transacciones else 0
    ingresos = total_ventas  # En un caso más complejo, podrían ser diferentes
    egresos = total_ventas * 0.7 if total_ventas > 0 else 0  # Simulamos un 70% de costos sobre ventas
    balance = ingresos - egresos
    
    # Redondear valores para un mejor formato
    total_ventas = int(round(total_ventas))
    ingresos = int(round(ingresos))
    egresos = int(round(egresos))
    balance = int(round(balance))
    
    return render(request, 'Home/pagos.html', {
        'nombre_usuario': nombre_usuario,
        'pagos': pagos,
        'transacciones': transacciones,
        'total_ventas': total_ventas,
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': balance
    })

def bodeguero(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    # Verificar que el usuario sea bodeguero o administrador
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario not in ['Bodeguero', 'Administrador']:
        messages.warning(request, "No tienes permisos para acceder al panel de bodeguero")
        return redirect('index')
    
    # Obtener nombre de usuario para mostrar en la página
    nombre_usuario = request.session.get('nombre_usuario')
    
    # Obtener todos los pedidos
    try:
        # Obtener pedidos ordenados por fecha descendente (más recientes primero)
        # y excluir los pedidos con estado 'Entregado' a menos que sea administrador
        if tipo_usuario == 'Administrador':
            pedidos = Pedido.objects.select_related('cliente').all().order_by('-fecha_pedido')
        else:
            # Para bodegueros, enfocamos en pedidos pendientes, aprobados o en preparación
            pedidos = Pedido.objects.select_related('cliente').exclude(
                estado_pedido='Entregado'
            ).order_by('-fecha_pedido')
        
        # Para cada pedido, obtenemos sus detalles de manera eficiente
        for pedido in pedidos:
            detalles = DetalleProducto.objects.filter(pedido=pedido).select_related('producto')
            pedido.detalles = list(detalles)
    except Exception as e:
        print(f"Error al obtener pedidos: {e}")
        messages.error(request, "Ocurrió un error al cargar los pedidos")
        pedidos = []
    
    return render(request, 'Home/bodeguero.html', {
        'nombre_usuario': nombre_usuario,
        'pedidos': pedidos,
        'tipo_usuario': tipo_usuario
    })

def registro(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        rut_cliente = request.POST.get('rut_cliente')
        fecha_registro = request.POST.get('fecha_registro')
        recibe_ofertas = request.POST.get('recibe_ofertas')
        nombre_cliente = request.POST.get('nombre_cliente')
        apellido_cliente = request.POST.get('apellido_cliente')
        direccion = request.POST.get('direccion')
        telefono_cliente = request.POST.get('telefono_cliente')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        # Guardar valores para relleno en caso de error
        valores = {
            'rut_cliente': rut_cliente,
            'fecha_registro': fecha_registro,
            'recibe_ofertas': recibe_ofertas,
            'nombre_cliente': nombre_cliente,
            'apellido_cliente': apellido_cliente,
            'direccion': direccion,
            'telefono_cliente': telefono_cliente,
            'correo': correo
        }
        
        # Validaciones
        errores = []
        
        # Validar que todos los campos estén completos
        if not all([rut_cliente, fecha_registro, recibe_ofertas, nombre_cliente, 
                    apellido_cliente, direccion, telefono_cliente, correo, contrasena]):
            errores.append('Todos los campos son obligatorios')
        
        # Validar formato de RUT (simple validación)
        if not ('-' in rut_cliente and len(rut_cliente) >= 8 and len(rut_cliente) <= 12):
            errores.append('El formato del RUT debe ser 12345678-9')
            
        # Validar que el RUT no exista ya
        if not errores and Cliente.objects.filter(rut_cliente=rut_cliente).exists():
            errores.append('El RUT ya está registrado')
            
        # Validar que el correo no exista ya
        if not errores and Cliente.objects.filter(correo=correo).exists():
            errores.append('El correo ya está registrado')
            
        # Si hay errores, volver al formulario
        if errores:
            return render(request, 'Home/registro.html', {'errores': errores, 'valores': valores})
        
        # Si no hay errores, crear el cliente
        try:
            nuevo_cliente = Cliente(
                rut_cliente=rut_cliente,
                fecha_registro=fecha_registro,
                recibe_ofertas=recibe_ofertas,
                nombre_cliente=nombre_cliente,
                apellido_cliente=apellido_cliente,
                direccion=direccion,
                telefono_cliente=telefono_cliente,
                correo=correo,
                contrasena=contrasena
            )
            nuevo_cliente.save()
            
            # Autenticar al usuario recién registrado
            request.session['nombre_usuario'] = nombre_cliente
            request.session['tipo_usuario'] = 'cliente'
            request.session['id_usuario'] = nuevo_cliente.rut_cliente  # Usando rut_cliente en lugar de id_cliente
            
            # Redirigir a la página principal
            return redirect('index')
        except Exception as e:
            errores.append(f'Error al guardar: {str(e)}')
            return render(request, 'Home/registro.html', {'errores': errores, 'valores': valores})
    
    # Si es GET, mostrar el formulario vacío
    return render(request, 'Home/registro.html')

def carrito(request):
    # Get cart from session
    carrito = request.session.get('carrito', [])
    total_items = sum(item['cantidad'] for item in carrito) if carrito else 0
    nombre_usuario = request.session.get('nombre_usuario')
    
    # Calculate subtotal
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito) if carrito else 0
    
    # Apply discount: 25% off if 4 or more items in cart
    discount = 0
    if total_items >= 4:
        discount = subtotal * Decimal('0.25')
    
    total = subtotal - discount
    
    return render(request, 'Home/carrito.html', {
        'carrito': carrito,
        'total_items': total_items,
        'nombre_usuario': nombre_usuario,
        'subtotal': subtotal,
        'discount': discount,
        'total': total
    })

def agregar_al_carrito(request, id_producto):
    # Get product
    producto = get_object_or_404(Producto, id_producto=id_producto)
    
    # Get or initialize cart
    carrito = request.session.get('carrito', [])
    
    # Check if product already in cart
    found = False
    for item in carrito:
        if item['id'] == id_producto:
            item['cantidad'] += 1
            found = True
            break
    
    # If not found, add new item
    if not found:
        carrito.append({
            'id': id_producto,
            'nombre': producto.nombre_producto,
            'precio': float(producto.precio_unitario),
            'cantidad': 1,
            'imagen': producto.imagen.url if producto.imagen else None
        })
    
    # Save to session
    request.session['carrito'] = carrito
    
    # Show message
    messages.success(request, f'"{producto.nombre_producto}" añadido al carrito.')
    
    # Redirect to previous page or products page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('productos')

def remove_from_cart(request, id_producto):
    # Get cart
    carrito = request.session.get('carrito', [])
    
    # Remove product
    carrito = [item for item in carrito if item['id'] != id_producto]
    
    # Save to session
    request.session['carrito'] = carrito
    
    # Redirect
    return redirect('carrito')

def cerrar_sesion(request):
    # Clear session
    request.session.flush()
    return redirect('index')

def empleados_direct(request):
    empleados = Empleado.objects.select_related('sucursal', 'cargo').all()
    return render(request, 'Home/empleados_direct.html', {'empleados': empleados})

def api_empleados_django(request):
    empleados = Empleado.objects.select_related('sucursal', 'cargo').all()
    empleados_data = []
    for emp in empleados:
        empleados_data.append({
            'id': emp.id_empleado,
            'nombre': emp.nombre_empleado,
            'apellido': emp.apellido_empleado,
            'correo': emp.correo,
            'sucursal': emp.sucursal.nombre_sucursal,
            'cargo': emp.cargo.nombre_cargo
        })
    return JsonResponse({'empleados': empleados_data})

def checkout(request):
    if 'carrito' not in request.session or not request.session['carrito']:
        return redirect('carrito')
    
    carrito = request.session['carrito']
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    # Apply discount
    total_items = sum(item['cantidad'] for item in carrito)
    discount = subtotal * Decimal('0.25') if total_items >= 4 else 0
    
    total = subtotal - discount
    
    # Get client
    nombre_usuario = request.session.get('nombre_usuario')
    try:
        cliente = Cliente.objects.get(nombre_cliente=nombre_usuario)
    except Cliente.DoesNotExist:
        return redirect('inicio')
    
    # Create PayPal payment
    payment_url, payment_id = crear_pago(
        total, 
        f'Compra Ferremax - {nombre_usuario}',
        request.build_absolute_uri(reverse('ejecutar_pago'))
    )
    
    if not payment_url or not payment_id:
        messages.error(request, "Error al crear el pago. Intente nuevamente.")
        return redirect('carrito')
    
    # Store payment_id in session
    request.session['paypal_payment_id'] = payment_id
    request.session['order_total'] = float(total)
    
    return redirect(payment_url)

def ejecutar_pago_view(request):
    payment_id = request.session.get('paypal_payment_id')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, "Error en la información de pago. Intente nuevamente.")
        return redirect('carrito')
    
    # Execute payment
    success, payment_details = ejecutar_pago(payment_id, payer_id)
    
    if not success:
        messages.error(request, "Error al procesar el pago. Intente nuevamente.")
        return redirect('carrito')
    
    # Get order data
    carrito = request.session.get('carrito', [])
    nombre_usuario = request.session.get('nombre_usuario')
    total = request.session.get('order_total', 0)
    
    try:
        # Get client
        cliente = Cliente.objects.get(nombre_cliente=nombre_usuario)
        
        # Create order
        pedido = Pedido.objects.create(
            cliente=cliente,
            tipo_entrega='Despacho',  # Default
            estado_pedido='Aprobado',
            paypal_payment_id=payment_id,
            total=total
        )
        
        # Add products to order
        for item in carrito:
            producto = Producto.objects.get(id_producto=item['id'])
            DetalleProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            
            # Update stock
            producto.stock_total -= item['cantidad']
            producto.save()
        
        # Clear cart
        request.session['carrito'] = []
        
        # Redirect to confirmation page
        return redirect('confirmacion_pedido', id_pedido=pedido.id_pedido)
        
    except Cliente.DoesNotExist:
        messages.error(request, "Error al identificar el cliente. Intente nuevamente.")
        return redirect('carrito')
    except Exception as e:
        messages.error(request, f"Error al procesar la orden: {str(e)}")
        return redirect('carrito')

def confirmacion_pedido(request, id_pedido):
    try:
        pedido = Pedido.objects.get(id_pedido=id_pedido)
        detalles = DetalleProducto.objects.filter(pedido=pedido)
        
        return render(request, 'Home/confirmacion_pedido.html', {
            'pedido': pedido,
            'detalles': detalles,
            'nombre_usuario': request.session.get('nombre_usuario')
        })
    except Pedido.DoesNotExist:
        return redirect('index')

def cambiar_estado_pedido(request, id_pedido):
    if request.method == 'POST' and request.session.get('tipo_usuario') in ['Administrador', 'Vendedor', 'Bodeguero']:
        # Comprobar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        
        if is_ajax:
            try:
                data = json.loads(request.body)
                nuevo_estado = data.get('nuevo_estado')
            except:
                nuevo_estado = None
        else:
            nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado in ['Pendiente', 'Aprobado', 'Rechazado', 'Enviado', 'Entregado', 'Preparado']:
            try:
                pedido = get_object_or_404(Pedido, id_pedido=id_pedido)
                pedido.estado_pedido = nuevo_estado
                pedido.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'estado': nuevo_estado,
                        'mensaje': f'El estado del pedido #{id_pedido} ha sido actualizado a {nuevo_estado}'
                    })
                
                # Redireccionar según el tipo de usuario
                if request.session.get('tipo_usuario') == 'Bodeguero':
                    messages.success(request, f'El estado del pedido #{id_pedido} ha sido actualizado a {nuevo_estado}')
                    return redirect('bodeguero')
            except Exception as e:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
        elif is_ajax:
            return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)
    
    return redirect('pedidos')

def check_stock(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_producto = data.get('id_producto')
        cantidad = data.get('cantidad', 1)
        
        try:
            producto = Producto.objects.get(id_producto=id_producto)
            return JsonResponse({
                'success': True,
                'stock': producto.stock_total,
                'available': producto.stock_total >= cantidad
            })
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def api_dolar(request):
    return render(request, 'apidolar.html')

def api_dolar_json(request):
    # Mock API response
    return JsonResponse({
        'dolar': {
            'valor': 850,
            'fecha': date.today().strftime('%Y-%m-%d')
        }
    })

def crearproductos(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session.get('tipo_usuario') not in ['Administrador', 'Vendedor']:
        return redirect('index')
    
    if request.method == 'POST':
        # Process form
        pass
    
    return render(request, 'Home/crearproductos.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })

def mis_productos(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session.get('tipo_usuario') not in ['Administrador', 'Vendedor']:
        return redirect('index')
    
    # Get created products
    productos = Producto.objects.all()
    
    return render(request, 'Home/mis_productos.html', {
        'nombre_usuario': request.session.get('nombre_usuario'),
        'productos': productos
    })

def modificar_producto(request, id_producto):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session.get('tipo_usuario') not in ['Administrador', 'Vendedor']:
        return redirect('index')
    
    producto = get_object_or_404(Producto, id_producto=id_producto)
    
    if request.method == 'POST':
        # Process form
        pass
    
    return render(request, 'Home/modificar_producto.html', {
        'nombre_usuario': request.session.get('nombre_usuario'),
        'producto': producto
    })

def eliminar_producto(request, id_producto):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    if request.session.get('tipo_usuario') not in ['Administrador', 'Vendedor']:
        return redirect('index')
    
    producto = get_object_or_404(Producto, id_producto=id_producto)
    producto.delete()
    
    messages.success(request, f'El producto "{producto.nombre_producto}" ha sido eliminado.')
    return redirect('mis_productos')

def herramientas(request):
    return render(request, 'Home/herramientas.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })

def mis_pedidos(request):
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
    
    nombre_usuario = request.session.get('nombre_usuario')
    
    try:
        cliente = Cliente.objects.get(nombre_cliente=nombre_usuario)
        pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
    except Cliente.DoesNotExist:
        pedidos = []
    
    return render(request, 'Home/mis_pedidos.html', {
        'nombre_usuario': nombre_usuario,
        'pedidos': pedidos
    })

def productos(request):
    # Get products
    productos = Producto.objects.all()
    
    # Get cart info for header
    carrito = request.session.get('carrito', [])
    total_items = sum(item['cantidad'] for item in carrito) if carrito else 0
    
    return render(request, 'Home/productos.html', {
        'productos': productos,
        'nombre_usuario': request.session.get('nombre_usuario'),
        'tipo_usuario': request.session.get('tipo_usuario'),
        'total_items': total_items
    })

def productosapi(request):
    return render(request, 'Home/productos_api.html')