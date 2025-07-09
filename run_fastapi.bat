@echo off
echo =============================================
echo Starting FastAPI server for Ferremax...
echo =============================================
echo.
echo Employee API:
echo - Access at: http://localhost:8001/api/empleados/
echo - View in browser: http://localhost:8001/empleados-web
echo.
echo Products API:
echo - Access at: http://localhost:8001/api/productos/
echo - View in browser: http://localhost:8001/productosapi
echo.
echo Documentation: http://localhost:8001/docs
echo.
echo Close this window to stop the server.
echo =============================================
cd %~dp0
set PYTHONPATH=%~dp0
venv\Scripts\python.exe appFerremax\fastapi_app.py
pause
