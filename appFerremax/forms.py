from django import forms
from .models import Producto, Sucursal
from decimal import Decimal
from django.core.exceptions import ValidationError
from appFerremax.models import Cliente
from django.core.mail import send_mail
from django.core import signing
import re
from datetime import date, datetime


class ProductoForm(forms.ModelForm):
    def clean_precio_unitario(self):
        """
        Limpia y convierte el precio unitario de formato '2.000' a Decimal
        """
        precio = self.cleaned_data.get('precio_unitario')
        if precio:
            if isinstance(precio, str):
                # Eliminar puntos de miles y reemplazar coma por punto si existe
                precio = precio.replace('.', '').replace(',', '.')
                try:
                    return Decimal(precio)
                except:
                    raise forms.ValidationError('Ingrese un precio válido')
        return precio
        
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'marca', 'precio_unitario', 
                  'stock_total', 'sucursal', 'imagen']
        
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taladro Bosch'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Breve descripción del producto'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Bosch'
            }),
            'precio_unitario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2.000',
                'inputmode': 'numeric',
                'pattern': '[0-9,.]*',
                'data-type': 'currency'
            }),
            'stock_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 10'
            }),
            'sucursal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'required': True
            }),
        }

class ClientePasswordResetForm(forms.Form):
    email = forms.EmailField(label="Correo", max_length=100)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Cliente.objects.filter(correo=email).exists():
            raise ValidationError("No existe un cliente registrado con este correo.")
        return email

    def save(self, domain_override=None, **kwargs):
        email = self.cleaned_data['email']
        cliente = Cliente.objects.get(correo=email)

        # Generar un token seguro con la librería signing
        token = signing.dumps({'correo': cliente.correo})

        link = f'http://127.0.0.1:8000/recuperar-contrasena/confirmar/{token}/'

        send_mail(
            'Recuperación de contraseña Ferremax',
            f'Hola {cliente.nombre_cliente}, haz clic en este enlace para restablecer tu contraseña: {link}',
            'azizoazoa@gmail.com',
            [cliente.correo],
            fail_silently=False,
        )


class CambiarContrasenaForm(forms.Form):
    nueva_contrasena = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("nueva_contrasena")
        pass2 = cleaned_data.get("confirmar_contrasena")

        if pass1 != pass2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data


class RegistroClienteForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Mínimo 8 caracteres, al menos una mayúscula y un número."
    )

    class Meta:
        model = Cliente
        fields = [
            'rut_cliente', 'fecha_registro', 'recibe_ofertas',
            'nombre_cliente', 'apellido_cliente', 'direccion',
            'telefono_cliente', 'correo', 'contrasena'
        ]

    def clean_rut_cliente(self):
        rut = self.cleaned_data['rut_cliente']
        rut_pattern = r"^\d{7,8}-[\dkK]$"
        if not re.match(rut_pattern, rut):
            raise ValidationError('RUT inválido: formato 12345678-9')
        # Aquí puedes agregar validación dígito verificador si quieres
        return rut

    def clean_fecha_registro(self):
        fecha = self.cleaned_data['fecha_registro']
        hoy = date.today()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad < 18:
            raise ValidationError('Debe ser mayor de edad para registrarse.')
        return fecha

    def clean_nombre_cliente(self):
        nombre = self.cleaned_data['nombre_cliente']
        if not nombre.strip():
            raise ValidationError('El nombre no puede estar vacío.')
        if re.search(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', nombre):
            raise ValidationError('Solo letras y espacios permitidos en nombre.')
        return nombre

    def clean_apellido_cliente(self):
        apellido = self.cleaned_data['apellido_cliente']
        if not apellido.strip():
            raise ValidationError('El apellido no puede estar vacío.')
        if re.search(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', apellido):
            raise ValidationError('Solo letras y espacios permitidos en apellido.')
        return apellido

    def clean_telefono_cliente(self):
        telefono = self.cleaned_data['telefono_cliente']
        if not telefono.isdigit():
            raise ValidationError('Teléfono debe contener solo números.')
        if len(telefono) < 8 or len(telefono) > 15:
            raise ValidationError('Teléfono con longitud incorrecta.')
        return telefono

    def clean_recibe_ofertas(self):
        valor = self.cleaned_data['recibe_ofertas']
        if valor not in ['S', 'N']:
            raise ValidationError('El campo recibe_ofertas debe ser "S" o "N".')
        return valor

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Cliente.objects.filter(correo=correo).exists():
            raise ValidationError('El correo ya está registrado.')
        return correo

    def save(self, commit=True):
        cliente = super().save(commit=False)
        # Hashea la contraseña antes de guardar
        from django.contrib.auth.hashers import make_password
        cliente.contrasena = make_password(self.cleaned_data['contrasena'])
        if commit:
            cliente.save()
        return cliente