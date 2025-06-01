# 🛠️ Ferremax

Ferremax es una aplicación web de ferretería desarrollada con Django y Oracle. Permite gestionar productos, clientes, empleados y mucho más.

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

### 4. Configura la base de datos Oracle

Edita el archivo `PaginaFerremax/settings.py` y asegúrate de que la sección `DATABASES` tenga tus datos de conexión a Oracle:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'orcl',  # o el nombre de tu servicio
        'USER': 'BDFerremas',
        'PASSWORD': 'BDFerremas',
        'HOST': 'localhost',
        'PORT': '1521',
    }
}
```

### 5. Aplica las migraciones para crear la base de datos y cargar datos iniciales

```bash
python manage.py migrate
```
Esto creará todas las tablas y cargará automáticamente las comunas y cargos necesarios para la aplicación.

### 6. (Opcional) Crea un superusuario para acceder al panel de administración

```bash
python manage.py createsuperuser
```

### 7. Ejecuta el servidor de desarrollo

```bash
python manage.py runserver
```

### 8. Accede a la aplicación

Abre tu navegador y visita:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📁 Estructura del proyecto

- `PaginaFerremax/` - Configuración principal del proyecto Django
- `appFerremax/` - Aplicación principal (modelos, vistas, templates, migraciones, etc.)
- `requirements.txt` - Dependencias del proyecto

## ⚠️ Notas importantes

- **No subas el archivo `db.sqlite3`** al repositorio. Este proyecto usa Oracle, no SQLite.
- Los datos de comunas y cargos se cargan automáticamente al ejecutar las migraciones.
- Si necesitas recargar comunas y cargos, ejecuta nuevamente las migraciones o consulta el admin de Django.
- Si usas archivos estáticos personalizados, ejecuta:
  ```bash
  python manage.py collectstatic
  ```

## 📞 Soporte

¿Dudas o problemas? Contacta al equipo de desarrollo o abre un issue en este repositorio.

---

¡Gracias por usar Ferremax! 🛒🔧
