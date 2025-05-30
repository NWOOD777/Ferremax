from django.db import models

class Comuna(models.Model):
    id_comuna = models.AutoField(primary_key=True)
    nombre_comuna = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_comuna

class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_sucursal

class Cargo(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    nombre_cargo = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_cargo

class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    nombre_empleado = models.CharField(max_length=100)
    apellido_empleado = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre_empleado} {self.apellido_empleado}"

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, self.correo):
            raise ValidationError('El correo no tiene un formato válido.')
        if len(self.contrasena) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not self.nombre_empleado.strip():
            raise ValidationError('El nombre no puede estar vacío.')
        if not self.apellido_empleado.strip():
            raise ValidationError('El apellido no puede estar vacío.')

class Cliente(models.Model):
    rut_cliente = models.CharField(primary_key=True, max_length=12)
    fecha_registro = models.DateField()
    recibe_ofertas = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=20)
    apellido_cliente = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50)
    telefono_cliente = models.CharField(max_length=20)
    correo = models.EmailField(unique=True, max_length=100)

    def __str__(self):
        return self.nombre_cliente

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        # Validar RUT chileno básico
        rut_pattern = r"^\d{7,8}-[\dkK]$"
        if not self.rut_cliente or not re.match(rut_pattern, self.rut_cliente):
            raise ValidationError('El RUT es obligatorio y debe tener formato 12345678-9.')
        if len(self.telefono_cliente) < 8:
            raise ValidationError('El teléfono debe tener al menos 8 dígitos.')
        if self.recibe_ofertas not in ['S', 'N']:
            raise ValidationError('El campo recibe_ofertas debe ser "S" o "N".')
        if not self.nombre_cliente.strip():
            raise ValidationError('El nombre no puede estar vacío.')
        if not self.apellido_cliente.strip():
            raise ValidationError('El apellido no puede estar vacío.')

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    marca = models.CharField(max_length=50)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock_total = models.IntegerField()
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_producto

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.nombre_producto.strip():
            raise ValidationError('El nombre del producto no puede estar vacío.')
        if self.stock_total < 0:
            raise ValidationError('El stock no puede ser negativo.')
        if self.precio_unitario <= 0:
            raise ValidationError('El precio debe ser mayor a cero.')

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    fecha_pedido = models.DateField()
    estado_pedido = models.CharField(max_length=20)
    tipo_entrega = models.CharField(max_length=20)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido {self.id_pedido}"

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        ESTADOS = ['Pendiente', 'Aprobado', 'Rechazado', 'Enviado', 'Entregado']
        TIPOS = ['Retiro', 'Despacho']
        if self.fecha_pedido > date.today():
            raise ValidationError('La fecha del pedido no puede ser futura.')
        if self.estado_pedido not in ESTADOS:
            raise ValidationError(f'El estado debe ser uno de: {", ".join(ESTADOS)}.')
        if self.tipo_entrega not in TIPOS:
            raise ValidationError('El tipo de entrega debe ser "Retiro" o "Despacho".')

class DetalleProducto(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')
        if self.producto and self.cantidad > self.producto.stock_total:
            raise ValidationError('La cantidad no puede superar el stock disponible.')

class Envio(models.Model):
    id_envio = models.AutoField(primary_key=True)
    fecha_envio = models.DateField()
    direccion_entrega = models.CharField(max_length=200)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)

class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    nombre_metodo_pago = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_metodo_pago

class EstadoPago(models.Model):
    id_estado_pago = models.AutoField(primary_key=True)
    estado_pago = models.CharField(max_length=20)

    def __str__(self):
        return self.estado_pago

class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    fecha = models.DateField()
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    estado_pago = models.ForeignKey(EstadoPago, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pago {self.id_pago}"

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        if self.fecha > date.today():
            raise ValidationError('La fecha de pago no puede ser futura.')