from django import forms
from .models import Producto, Sucursal

class ProductoForm(forms.ModelForm):
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
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 19990'
            }),
            'stock_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 10'
            }),
            'sucursal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }