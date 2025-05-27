from django.db import models

# Create your models here.
class Empleado(models.Model):
    rut_empleado = models.CharField(max_length=12, unique=True)
    nombre_empleado = models.CharField(max_length=100)
    apellido_empleado = models.CharField(max_length=100)
    email_empleado = models.EmailField()
    telefono_empleado = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.rut_empleado}"
    
class Cliente(models.Model):
    rut_cliente = models.CharField(max_length=12, unique=True)
    nombre_cliente = models.CharField(max_length=100)
    apellido_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.rut_cliente}"