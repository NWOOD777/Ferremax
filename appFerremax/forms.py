from django import forms
from .models import Producto, Sucursal
from decimal import Decimal
from django.core.exceptions import ValidationError
from appFerremax.models import Cliente
from django.core.mail import send_mail
from django.core import signing


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