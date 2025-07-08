@echo off
echo =============================================
echo Starting FastAPI server for Ferremax...
echo =============================================
echo.
echo Access the API at: http://localhost:8000/api/empleados/
echo Access the Swagger docs at: http://localhost:8000/docs
echo Access the HTML page at: http://localhost:8000/empleados-web
echo.
echo Close this window to stop the server.
echo =============================================
cd %~dp0
set PYTHONPATH=%~dp0
venv\Scripts\python.exe appFerremax\fastapi_app.py
pause
