from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.views.defaults import page_not_found
import json
from decimal import Decimal, InvalidOperation
from datetime import date
from .forms import ProductoForm

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
                    request.session['correo'] = cliente.correo  # Guardar el correo para identificación única
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
                        request.session['correo'] = empleado.correo  # Guardar el correo para identificación única
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
            correo_cliente = request.session.get('correo')
            
            # Primero buscar por correo si está disponible (más confiable)
            if correo_cliente:
                cliente = Cliente.objects.filter(correo=correo_cliente).first()
                if not cliente:
                    # Si no encuentra por correo, buscar por nombre
                    cliente = Cliente.objects.filter(nombre_cliente=nombre_cliente).first()
            else:
                # Si no hay correo en sesión, buscar por nombre
                cliente = Cliente.objects.filter(nombre_cliente=nombre_cliente).first()
                
            if not cliente:
                return redirect('inicio')  
                
            pedidos_cliente = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
            
            return render(request, 'Home/pedidos.html', {
                'pedidos': pedidos_cliente
            })
        except Exception as e:
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
            request.session['correo'] = correo  # Guardar el correo para identificación única
            
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
    
    # Calculate subtotal - asegurándonos que sea Decimal
    subtotal = Decimal('0')
    
    # Enrich cart items with stock information
    productos_problematicos = []
    for item in carrito:
        # Convertir precio y cantidad a Decimal para evitar problemas de tipo
        precio = Decimal(str(item['precio']))
        cantidad = Decimal(str(item['cantidad']))
        subtotal += precio * cantidad
        
        # Get current stock from database
        try:
            producto = Producto.objects.get(id_producto=item['id'])
            item['stock'] = producto.stock_total
            
            # Check for negative or low stock
            if producto.stock_total < 0:
                productos_problematicos.append({
                    'id': producto.id_producto,
                    'nombre': producto.nombre_producto,
                    'stock_actual': producto.stock_total,
                    'cantidad_solicitada': item['cantidad'],
                    'tipo': 'negativo'
                })
            elif producto.stock_total < item['cantidad']:
                productos_problematicos.append({
                    'id': producto.id_producto,
                    'nombre': producto.nombre_producto,
                    'stock_actual': producto.stock_total,
                    'cantidad_solicitada': item['cantidad'],
                    'tipo': 'insuficiente'
                })
        except Producto.DoesNotExist:
            item['stock'] = 0
            productos_problematicos.append({
                'id': item['id'],
                'nombre': item['nombre'],
                'stock_actual': 0,
                'cantidad_solicitada': item['cantidad'],
                'tipo': 'no_existe'
            })
    
    # Apply discount: 25% off if 4 or more items in cart
    discount = Decimal('0')
    if total_items >= 4:
        discount = subtotal * Decimal('0.25')
    
    # Calcular el total final como Decimal
    total = subtotal - discount
    
    return render(request, 'Home/carrito.html', {
        'carrito': carrito,
        'total_items': total_items,
        'nombre_usuario': nombre_usuario,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'productos_problematicos': productos_problematicos
    })

def agregar_al_carrito(request, id_producto):
    # Get product
    producto = get_object_or_404(Producto, id_producto=id_producto)
    
    # Get or initialize cart
    carrito = request.session.get('carrito', [])
    
    # Check if it's a POST request from the cart page with a specific quantity
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get the requested quantity from POST data
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            # Find and update the product in cart
            found = False
            for item in carrito:
                if item['id'] == id_producto:
                    item['cantidad'] = nueva_cantidad  # Set to the exact quantity provided
                    found = True
                    break
            
            # If not found, add new item with the requested quantity
            if not found:
                carrito.append({
                    'id': id_producto,
                    'nombre': producto.nombre_producto,
                    'precio': float(producto.precio_unitario),
                    'cantidad': nueva_cantidad,
                    'imagen': producto.imagen.url if producto.imagen else None
                })
                
            # Save to session
            request.session['carrito'] = carrito
            
            # Return success response for AJAX request
            return JsonResponse({'status': 'success', 'message': f'Cantidad actualizada: {nueva_cantidad}'})
            
        except (ValueError, TypeError) as e:
            # Handle invalid quantity
            return JsonResponse({'status': 'error', 'message': 'Cantidad inválida'}, status=400)
    
    # Handle AJAX GET requests (from productos.html)
    elif request.GET.get('ajax') == 'true':
        # Check if product already in cart
        found = False
        for item in carrito:
            if item['id'] == id_producto:
                item['cantidad'] += 1  # Increment by 1
                found = True
                break
        
        # If not found, add new item with quantity 1
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
        
        # Calculate total items
        total_items = sum(item['cantidad'] for item in carrito)
        
        # Return JSON response for AJAX
        return JsonResponse({
            'success': True, 
            'message': f'"{producto.nombre_producto}" añadido al carrito.',
            'total_items': total_items
        })
    
    # Regular GET request handling (adding single item to cart)
    else:
        # Check if product already in cart
        found = False
        for item in carrito:
            if item['id'] == id_producto:
                item['cantidad'] += 1  # Increment by 1
                found = True
                break
        
        # If not found, add new item with quantity 1
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
        
        # Show message for regular page navigation
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
    correo_usuario = request.session.get('correo')
    
    try:
        # Primero intentar obtener el cliente por correo (que es único)
        if correo_usuario:
            cliente = Cliente.objects.filter(correo=correo_usuario).first()
            if not cliente:
                # Si no se encuentra por correo, buscar por nombre pero usando filter().first()
                cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
        else:
            # Si no hay correo en la sesión, buscar por nombre usando filter().first()
            cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
            
        if not cliente:
            messages.error(request, "No se pudo identificar al cliente. Por favor, intente iniciar sesión nuevamente.")
            return redirect('inicio')
    except Exception as e:
        messages.error(request, f"Error al identificar al cliente: {str(e)}")
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
        # Primero intentar obtener el cliente por correo (que es único)
        correo_usuario = request.session.get('correo')
        if correo_usuario:
            cliente = Cliente.objects.filter(correo=correo_usuario).first()
            if not cliente:
                # Si no se encuentra por correo, buscar por nombre pero usando filter().first()
                cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
        else:
            # Si no hay correo en la sesión, buscar por nombre usando filter().first()
            cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
            
        if not cliente:
            messages.error(request, "No se pudo identificar al cliente. Por favor, intente iniciar sesión nuevamente.")
            return redirect('carrito')
        
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
                cantidad=item['cantidad']
                # No usar precio_unitario ya que no existe la columna en la BD
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
    
    mensaje = None
    
    if request.method == 'POST':
        # Importar aquí para evitar importación circular
        from .forms import ProductoForm
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar pero no hacer commit para añadir datos adicionales
            producto = form.save(commit=False)
            # Verificar que la imagen está presente
            if not request.FILES.get('imagen'):
                form.add_error('imagen', 'La imagen es obligatoria')
            else:
                # Intentar obtener el id del usuario de la sesión
                id_usuario = request.session.get('id_usuario')
                
                # Si tenemos un ID de empleado, intentar asignar el creador
                if id_usuario:
                    try:
                        empleado = Empleado.objects.get(id_empleado=id_usuario)
                        producto.creado_por = empleado
                    except Empleado.DoesNotExist:
                        # Si no existe, continuamos sin asignar creador
                        pass
                
                # Asignar fecha de creación
                producto.fecha_creacion = timezone.now()
                
                # Guardar el producto
                producto.save()
                mensaje = "Producto creado exitosamente"
                # Redirigir o crear nuevo formulario
                form = ProductoForm()
    else:
        # Importar aquí para evitar importación circular
        from .forms import ProductoForm
        form = ProductoForm()
    
    return render(request, 'Home/crearproductos.html', {
        'nombre_usuario': request.session.get('nombre_usuario'),
        'form': form,
        'mensaje': mensaje
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
    mensaje = None
    actualizado = False
    
    if request.method == 'POST':
        # Procesar el formulario con los datos enviados
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            mensaje = "El producto ha sido actualizado correctamente"
            actualizado = True
    else:
        # Crear el formulario con la instancia del producto existente
        form = ProductoForm(instance=producto)
    
    return render(request, 'Home/modificar_producto.html', {
        'nombre_usuario': request.session.get('nombre_usuario'),
        'producto': producto,
        'form': form,
        'mensaje': mensaje,
        'actualizado': actualizado
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
    correo_usuario = request.session.get('correo')
    
    # Check if we have correo in session, which is more unique
    if correo_usuario:
        try:
            # Use correo if available
            cliente = Cliente.objects.filter(correo=correo_usuario).first()
            if cliente:
                pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
            else:
                pedidos = []
        except Exception as e:
            print(f"Error al buscar cliente por correo: {e}")
            pedidos = []
    else:
        # Fallback to using nombre_cliente but get first match instead of get()
        try:
            clientes = Cliente.objects.filter(nombre_cliente=nombre_usuario)
            if clientes.exists():
                cliente = clientes.first()  # Just use the first matching client
                pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
            else:
                pedidos = []
        except Exception as e:
            print(f"Error al buscar cliente por nombre: {e}")
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
    
def vista_404_test(request):
    """
    Vista para probar la página 404 en modo de desarrollo
    """
    # Mostrar la página 404 personalizada
    return page_not_found(request, Exception("Esta es una prueba de la página 404"))

def handler404(request, exception=None):
    """
    Manejador personalizado para errores 404
    """
    return render(request, '404.html', {'path': request.path}, status=404)

def test_404(request):
    """
    Vista para probar la página 404 incluso con DEBUG=True
    """
    return handler404(request)

def handler500(request):
    """
    Manejador personalizado para errores 500
    """
    return render(request, '404.html', {'path': request.path, 'error_type': '500 - Error Interno del Servidor'}, status=500)

def handler403(request, exception=None):
    """
    Manejador personalizado para errores 403
    """
    return render(request, '404.html', {'path': request.path, 'error_type': '403 - Acceso Prohibido'}, status=403)

def handler400(request, exception=None):
    """
    Manejador personalizado para errores 400
    """
    return render(request, '404.html', {'path': request.path, 'error_type': '400 - Solicitud Incorrecta'}, status=400)

import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Cliente, Producto, Pedido, DetalleProducto

@csrf_exempt
@require_POST
def ejecutar_pago_ajax(request):
    """
    Procesa un pago de PayPal recibido vía AJAX
    """
    try:
        print("Iniciando procesamiento de pago via AJAX")
        
        # Obtener datos del cuerpo JSON
        data = json.loads(request.body)
        print(f"Datos recibidos: {data}")
        
        cart_items = data.get('cart', [])
        payment_id = data.get('payment_id')
        payer_id = data.get('payer_id')
        
        print(f"Cart items: {cart_items}")
        print(f"Payment ID: {payment_id}")
        print(f"Payer ID: {payer_id}")
        
        # Log detailed cart item information for debugging
        print("----- DETALLE DE ITEMS EN EL CARRITO -----")
        for i, item in enumerate(cart_items):
            quantity = int(item.get('quantity', 0))
            print(f"Item {i+1}: ID={item['id']}, Nombre={item.get('nombre', 'N/A')}, Price={item.get('price', 0)}, Cantidad={quantity}")
        print("------------------------------------------")
        
        if not cart_items or not payment_id or not payer_id:
            print("Error: Datos incompletos para procesar el pago")
            return JsonResponse({
                'success': False, 
                'error': 'Datos incompletos para procesar el pago'
            }, status=400)
        
        # Calcular el total del carrito usando Decimal para evitar problemas de tipos
        total = Decimal('0')
        for item in cart_items:
            price = Decimal(str(item['price']))
            quantity = Decimal(str(item['quantity']))
            total += price * quantity
        
        # Aplicar descuento si hay 4 o más productos
        total_items = sum(int(item['quantity']) for item in cart_items)
        if total_items >= 4:
            total = total * Decimal('0.75')  # 25% de descuento
        
        # Verificar si hay usuario autenticado
        if 'nombre_usuario' not in request.session:
            return JsonResponse({
                'success': False, 
                'error': 'Usuario no autenticado'
            }, status=403)
            
        nombre_usuario = request.session.get('nombre_usuario')
        
        try:
            # Primero intentar obtener el cliente por correo (que es único)
            correo_usuario = request.session.get('correo')
            if correo_usuario:
                cliente = Cliente.objects.filter(correo=correo_usuario).first()
                if not cliente:
                    # Si no se encuentra por correo, buscar por nombre pero usando filter().first()
                    cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
            else:
                # Si no hay correo en la sesión, buscar por nombre usando filter().first()
                cliente = Cliente.objects.filter(nombre_cliente=nombre_usuario).first()
                
            if not cliente:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo identificar al cliente'
                }, status=404)
                
            # Crear el pedido
            # Asegurar que el total sea un Decimal con dos decimales
            total_decimal = Decimal(str(total)).quantize(Decimal('0.01'))
            
            pedido = Pedido.objects.create(
                cliente=cliente,
                tipo_entrega='Despacho',  # Valor predeterminado
                estado_pedido='Aprobado',
                paypal_payment_id=payment_id,
                total=total_decimal
            )
            
            # Verificar stock antes de procesar
            stock_issues = []
            for item in cart_items:
                product_id = int(item['id']) if isinstance(item['id'], str) else item['id']
                try:
                    producto = Producto.objects.get(id_producto=product_id)
                    item_quantity = int(item['quantity']) if str(item['quantity']).isdigit() else 1
                    
                    # Verificar si hay problemas de stock
                    if producto.stock_total < 0:
                        stock_issues.append(f"Producto '{producto.nombre_producto}' tiene stock negativo ({producto.stock_total}).")
                    elif producto.stock_total < item_quantity:
                        stock_issues.append(f"Stock insuficiente para '{producto.nombre_producto}'. Solicitado: {item_quantity}, Disponible: {producto.stock_total}.")
                except Producto.DoesNotExist:
                    stock_issues.append(f"El producto con ID {product_id} ya no existe en el catálogo.")
            
            # Si hay problemas de stock, no procesar el pedido
            if stock_issues:
                return JsonResponse({
                    'success': False,
                    'error': 'Problemas de stock detectados',
                    'details': stock_issues
                }, status=400)
            
            # Agregar productos al pedido
            for item in cart_items:
                # Asegurar que el ID sea un entero
                product_id = int(item['id']) if isinstance(item['id'], str) else item['id']
                producto = Producto.objects.get(id_producto=product_id)
                
                # Obtener la cantidad del item y asegurarse de que sea un entero válido
                item_quantity = int(item['quantity']) if str(item['quantity']).isdigit() else 1
                if item_quantity < 1:
                    print(f"ADVERTENCIA: Cantidad inválida ({item['quantity']}) para producto {producto.nombre_producto}, usando 1 en su lugar")
                    item_quantity = 1
                
                # Crear el detalle del producto sin usar precio_unitario
                detalle = DetalleProducto(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item_quantity,
                )
                
                # No usar precio_unitario ya que no existe la columna en la BD
                print(f"Creando detalle para producto {producto.nombre_producto}, cantidad: {detalle.cantidad} (original: {item['quantity']})")
                
                detalle.save()
                
                # Actualizar stock
                producto.stock_total -= int(item['quantity'])
                producto.save()
            
            # Limpiar el carrito en la sesión
            request.session['carrito'] = []
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'pedido_id': pedido.id_pedido,
                'mensaje': 'Pago procesado correctamente',
                'redirect_url': f'/confirmacion_pedido/{pedido.id_pedido}/'  # Redirigir a la página de confirmación del pedido
            })
            
        except Cliente.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cliente no encontrado'
            }, status=404)
            
        except Producto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Uno o más productos no existen'
            }, status=404)
            
        except Exception as e:
            print(f"Error al procesar el pedido: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar el pedido: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato JSON inválido'
        }, status=400)
    except Exception as e:
        print(f"Error general: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)