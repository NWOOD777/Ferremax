@echo off
echo Ejecutando comandos para cargar métodos de pago...
cd /d "d:\usuario\Descargas\Joaco\Duoc\5S\IP\Ferremax"
python manage.py cargar_metodos_pago
echo.
echo Si no hay errores, los métodos de pago se han cargado correctamente.
echo.
pause
