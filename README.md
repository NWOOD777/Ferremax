# 🛠️ Ferremax

Ferremax es una aplicación web de ferretería desarrollada con Django y Oracle. Permite gestionar productos, clientes, empleados y mucho más. Ahora también incluye una API REST construida con FastAPI para acceder a los datos de empleados.

## 🚀 Instalación y ejecución

Sigue estos pasos para ejecutar el proyecto en tu computador o presentarlo en cualquier PC:

### 1. Clona el repositorio

```bash
git clone https://github.com/NWOOD777/Ferremax.git
cd Ferremax
```

### 2. Crea y activa un entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplica las migraciones para crear la base de datos y cargar datos iniciales

```bash
python manage.py migrate
```
Esto creará todas las tablas y cargará automáticamente las comunas y cargos necesarios para la aplicación.


### 5. Ejecuta el servidor de desarrollo

```bash
python manage.py runserver
```

### 6. Accede a la aplicación

Accede a la aplicación web desde tu navegador en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 7. API FastAPI para Empleados (Opcional)

Para iniciar la API de FastAPI que muestra la información de empleados:

```bash
# Inicia la API en puerto 8000
python appFerremax/fastapi_app.py
```

O en Windows, simplemente ejecuta:
```bash
run_fastapi.bat
```

Una vez iniciada, puedes acceder a:
- Documentación interactiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Lista de empleados: [http://127.0.0.1:8000/api/empleados/](http://127.0.0.1:8000/api/empleados/)
- Detalles de un empleado: [http://127.0.0.1:8000/api/empleados/1](http://127.0.0.1:8000/api/empleados/1) (reemplaza 1 con el ID del empleado)

Abre tu navegador y visita:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📞 Soporte

¿Dudas o problemas? Contacta al equipo de desarrollo o abre un issue en este repositorio.

---

¡Gracias por usar Ferremax! 🛒🔧
