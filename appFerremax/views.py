from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests


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
    
    # Calculate total cart items for display
    carrito = request.session.get('carrito', [])
    total_items = sum(item['cantidad'] for item in carrito) if carrito else 0
    
    # Verificar si aplica descuento
    discount_eligible = total_items >= 4
    
    return render(request, 'Home/index.html', {
        'nombre_usuario': nombre_usuario, 
        'productos': productos,
        'total_cart_items': total_items,
        'discount_eligible': discount_eligible
    })




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
    # Verificar que el usuario esté autenticado y sea contador
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
        
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario != 'Contador':
        return redirect('index')
    
    # Obtener el nombre de usuario para mostrarlo en la página
    nombre_usuario = request.session.get('nombre_usuario')
    
    # Obtener pagos de la base de datos
    pagos_list = Pago.objects.all().order_by('-fecha')
    
    # Obtener todos los pedidos con sus detalles para tabla de transacciones
    transacciones = []
    # Obtenemos pedidos con pagos completados (incluye pagados pero no necesariamente entregados)
    pagos_completados = Pago.objects.filter(estado_pago__estado_pago='Completado')
    pedidos_pagados = [pago.pedido for pago in pagos_completados]
    
    for pedido in pedidos_pagados:
        detalles = DetalleProducto.objects.filter(pedido=pedido)
        for detalle in detalles:
            transacciones.append({
                'id': pedido.id_pedido,
                'fecha': pedido.fecha_pedido,
                'cliente': f"{pedido.cliente.nombre_cliente} {pedido.cliente.apellido_cliente}",
                'producto': detalle.producto.nombre_producto,
                'cantidad': detalle.cantidad,
                'total': detalle.cantidad * detalle.producto.precio_unitario
            })
    
    # Calcular totales para los informes financieros
    total_ventas = sum(t['total'] for t in transacciones)
    
    ingresos = sum(pago.pedido.total for pago in pagos_list if pago.estado_pago.estado_pago == 'Completado')
    egresos = 0  # Podría calcularse de otra tabla si existe

    # Balance final
    balance = ingresos - egresos
    
    return render(request, 'Home/pagos.html', {
        'nombre_usuario': nombre_usuario,
        'pagos': pagos_list,
        'transacciones': transacciones,
        'total_ventas': total_ventas,
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': balance
    })

def bodeguero(request):
    # Verificar que el usuario esté autenticado y sea bodeguero
    if 'nombre_usuario' not in request.session:
        return redirect('inicio')
        
    tipo_usuario = request.session.get('tipo_usuario')
    if tipo_usuario != 'Bodeguero':
        return redirect('index')
    
    # Obtener el nombre de usuario para mostrarlo en la página
    nombre_usuario = request.session.get('nombre_usuario')
    
    # Obtener los pedidos que no están completados aún
    pedidos = Pedido.objects.filter(estado_pedido__in=['Pendiente', 'Aprobado', 'Preparado'])
    
    # Cargar los detalles de cada pedido
    for pedido in pedidos:
        pedido.detalles = DetalleProducto.objects.filter(pedido=pedido)
        
    return render(request, 'Home/bodeguero.html', {
        'pedidos': pedidos,
        'nombre_usuario': nombre_usuario
    })

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

def agregar_al_carrito(request, id_producto):
    try:
        producto = get_object_or_404(Producto, id_producto=id_producto)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Inicializar el carrito si no existe
        if 'carrito' not in request.session:
            request.session['carrito'] = []
        
        carrito = request.session['carrito']
        
        # Determinar si la llamada viene de la página del carrito (actualización) o de otro lugar (adición)
        # Las actualizaciones desde el carrito envían la cantidad exacta, no un incremento
        is_update_from_cart = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Verificar si el producto ya está en el carrito
        encontrado = False
        for item in carrito:
            if item['id'] == id_producto:
                if is_update_from_cart:
                    # Si es una actualización desde la página del carrito, establecer la cantidad exacta
                    item['cantidad'] = cantidad
                else:
                    # Si es una adición normal desde otra página, incrementar la cantidad
                    item['cantidad'] += cantidad
                encontrado = True
                messages.success(request, f'Se actualizó la cantidad de {producto.nombre_producto} en el carrito.')
                break
        
        # Si no está en el carrito, agregarlo
        if not encontrado:
            # Aquí necesitamos manejar el caso donde imagen podría ser None
            imagen_url = ''
            if producto.imagen:
                try:
                    imagen_url = producto.imagen.url
                except:
                    # Si hay error al obtener la URL, dejamos vacío
                    pass
            
            carrito.append({
                'id': id_producto,
                'nombre': producto.nombre_producto,
                'precio': float(producto.precio_unitario),
                'cantidad': cantidad,
                'imagen': imagen_url,
            })
            messages.success(request, f'{producto.nombre_producto} agregado al carrito.')
        
        # Guardar el carrito actualizado en la sesión
        request.session['carrito'] = carrito
        request.session.modified = True
        
        # Verificar si es una solicitud AJAX
        is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax_request:
            # Si es una solicitud AJAX, devolver una respuesta JSON
            return JsonResponse({
                'success': True, 
                'message': 'Cantidad actualizada',
                'cantidad': cantidad
            })
    except Exception as e:
        error_msg = f'Error al agregar producto: {str(e)}'
        messages.error(request, error_msg)
        
        # Si es una solicitud AJAX, devolver el error como JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
    
    # Solo para solicitudes no AJAX: Redireccionar de vuelta a la página anterior
    return redirect('index')

def carrito(request):
    # Allow anyone to view cart even if not logged in
    # if 'nombre_usuario' not in request.session:
    #     return redirect('inicio')
    
    carrito = request.session.get('carrito', [])
    
    # Calcular el total
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    # Calcular el número total de productos en el carrito
    total_items = sum(item['cantidad'] for item in carrito)
    
    # Aplicar 25% de descuento si hay 4 o más productos en el carrito
    discount = 0
    if total_items >= 4:
        discount = total * 0.25  # 25% de descuento
        total_after_discount = total - discount
    else:
        total_after_discount = total
    
    return render(request, 'Home/carrito.html', {
        'carrito': carrito,
        'total': total,
        'total_items': total_items,
        'apply_discount': total_items >= 4,
        'discount_percentage': 25,
        'discount_amount': discount,
        'total_after_discount': total_after_discount
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
    
    # Contar productos para el descuento
    total_items = sum(item['cantidad'] for item in carrito)
    apply_discount = total_items >= 4
    
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
    
    # Aplicar descuento de 25% si hay 4 o más productos
    if apply_discount:
        discount = total * Decimal('0.25')
        total = total - discount
    
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

            # Verificar carrito vacío
            if not cart:
                # Si no hay carrito en la solicitud, intentar obtener de la sesión
                cart = request.session.get('carrito', [])
                if not cart:
                    return JsonResponse({'success': False, 'error': 'El carrito está vacío'})
                
            # Imprimir para depuración
            print("Estructura del carrito recibido:", cart)
            
            # Asegurarse de que el carrito tiene el formato correcto
            total = 0
            processed_cart = []
            
            for item in cart:
                try:
                    # Acceder a las propiedades según el formato del carrito
                    print(f"Item recibido: {item}")
                    
                    # Compatibilidad con diferentes formatos de carrito
                    item_id = item.get('id')
                    # Para el formato de carrito de sesión
                    quantity = int(item.get('quantity', item.get('cantidad', 1)))
                    price = float(item.get('price', item.get('precio', 0)))
                    
                    print(f"Procesando item: id={item_id}, quantity={quantity}, price={price}")
                    
                    if not item_id:
                        return JsonResponse({'success': False, 'error': 'ID de producto no encontrado en el carrito. Por favor, vuelva a agregar los productos.'})
                    
                    # Buscar el producto en la base de datos
                    try:
                        producto = Producto.objects.get(id_producto=item_id)
                        print(f"Producto encontrado: {producto.nombre_producto}, Stock actual: {producto.stock_total}, Cantidad solicitada: {quantity}")
                        
                        # Asegurarse de que stock_total es un entero
                        stock_total = int(producto.stock_total) if producto.stock_total is not None else 0
                        
                        # Verificar stock
                        if stock_total < quantity:
                            print(f"ERROR DE STOCK: {producto.nombre_producto} - Stock disponible: {stock_total}, Cantidad solicitada: {quantity}")
                            return JsonResponse({'success': False, 'error': f'No hay suficiente stock para {producto.nombre_producto} (Stock: {stock_total}, Solicitado: {quantity})'})
                            
                        # Verificar que el stock no sea negativo
                        if stock_total <= 0:
                            print(f"ERROR DE STOCK NEGATIVO: {producto.nombre_producto} - Stock disponible: {stock_total}")
                            return JsonResponse({'success': False, 'error': f'El producto {producto.nombre_producto} está fuera de stock'})
                    except Producto.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Producto ID:{item_id} no encontrado'})
                    except Exception as e:
                        print(f"Error al verificar stock: {str(e)}")
                        return JsonResponse({'success': False, 'error': f'Error verificando stock: {str(e)}'})

                    # Calcular subtotal y acumularlo
                    subtotal = price * quantity
                    total += subtotal
                    
                    # Guardar los datos procesados para usar más tarde
                    processed_cart.append({
                        'id': item_id,
                        'quantity': quantity,
                        'price': price,
                        'producto': producto
                    })
                    
                except Producto.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Producto ID:{item_id} no encontrado'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Error procesando el carrito: {str(e)}'})

            # Aplicar descuento de 25% si hay 4 o más productos
            total_items = sum(item['quantity'] for item in processed_cart)
            if total_items >= 4:
                discount = total * 0.25
                total = total - discount
            
            # Verificar total mayor a cero (usando el total calculado con los productos procesados)
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

            # Crea los detalles y actualiza stock usando el carrito procesado
            for item in processed_cart:
                producto = item['producto']
                DetalleProducto.objects.create(
                    cantidad=item['quantity'],
                    producto=producto,
                    pedido=pedido
                )
                producto.stock_total -= item['quantity']
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

            # Limpia el carrito en sesión
            if 'carrito' in request.session:
                del request.session['carrito']
                request.session.modified = True

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

def check_stock(request):
    """
    View to check the stock levels of all products.
    For debugging purposes.
    """
    productos = Producto.objects.all().order_by('stock_total')
    return render(request, 'Home/check_stock.html', {'productos': productos})

def api_dolar(request):
    """
    Vista para obtener el tipo de cambio actual de USD a CLP utilizando la API de ExchangeRate-API
    """
    try:
        # Llamada a la API gratuita de ExchangeRate-API
        response = requests.get('https://open.er-api.com/v6/latest/USD')
        data = response.json()
        
        # Verificar si la llamada fue exitosa
        if response.status_code == 200 and data.get('result') == 'success':
            # Obtener el tipo de cambio de USD a CLP
            usd_to_clp = data['rates'].get('CLP', 0)
            
            # Obtener tipos de cambio adicionales (opcional)
            usd_to_eur = data['rates'].get('EUR', 0)
            usd_to_gbp = data['rates'].get('GBP', 0)
            
            # Renderizar la plantilla con los datos
            return render(request, 'apidolar.html', {
                'usd_to_clp': usd_to_clp,
                'usd_to_eur': usd_to_eur,
                'usd_to_gbp': usd_to_gbp,
                'timestamp': data.get('time_last_update_utc', ''),
                'success': True
            })
        else:
            # En caso de error, mostrar mensaje
            return render(request, 'apidolar.html', {
                'error_message': 'No se pudo obtener el tipo de cambio. Intente nuevamente más tarde.',
                'success': False
            })
    except Exception as e:
        # En caso de error, mostrar mensaje
        return render(request, 'apidolar.html', {
            'error_message': f'Error al obtener el tipo de cambio: {str(e)}',
            'success': False
        })

def api_dolar_json(request):
    """
    Endpoint JSON para obtener el tipo de cambio actual de USD a CLP utilizando la API de ExchangeRate-API
    """
    try:
        # Llamada a la API gratuita de ExchangeRate-API
        response = requests.get('https://open.er-api.com/v6/latest/USD')
        data = response.json()
        
        # Verificar si la llamada fue exitosa
        if response.status_code == 200 and data.get('result') == 'success':
            # Obtener el tipo de cambio de USD a CLP
            usd_to_clp = data['rates'].get('CLP', 850)  # Valor predeterminado 850 si no se encuentra
            
            # Devolver respuesta JSON
            return JsonResponse({
                'success': True,
                'exchange_rate': usd_to_clp,
                'timestamp': data.get('time_last_update_utc', '')
            })
        else:
            # En caso de error, devolver mensaje de error
            return JsonResponse({
                'success': False,
                'error': 'No se pudo obtener el tipo de cambio'
            })
    except Exception as e:
        # En caso de error, devolver mensaje de error
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def remove_from_cart(request, id_producto):
    if 'carrito' in request.session:
        carrito = request.session['carrito']
        # Find the item by id
        for i, item in enumerate(carrito):
            if item['id'] == id_producto:
                del carrito[i]
                break
                
        # Update the session
        request.session['carrito'] = carrito
        request.session.modified = True
    
    return redirect('carrito')


