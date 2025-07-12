from django import forms
from .models import Producto, Sucursal
from decimal import Decimal

class ProductoForm(forms.ModelForm):
    def clean_precio_unitario(self):
        """
        Limpia y convierte el precio unitario de formato '2.000' a Decimal
        """
        precio = self.cleaned_data.get('precio_unitario')
        if precio:
            # Si es una cadena (viene con formato), limpiamos y convertimos
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
        
        # Define widgets personalizados con clases Bootstrap
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
                'inputmode': 'numeric',  # Muestra un teclado numérico en dispositivos móviles
                'pattern': '[0-9,.]*',    # Solo permite números, comas y puntos
                'data-type': 'currency'  # Para uso con JS si necesitamos formatear
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