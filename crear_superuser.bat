@echo off
echo Creando superusuario predefinido para Ferremax...
cd /d "d:\usuario\Descargas\Joaco\Duoc\5S\IP\Ferremax"
python manage.py crear_superusuario
echo.
echo Si no hay errores, el superusuario ha sido creado correctamente.
echo Usuario: admin
echo Contraseña: ferremax2025
echo.
pause
