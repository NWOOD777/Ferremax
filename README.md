# 🛠️ Ferremax

Ferremax es una aplicación web de ferretería desarrollada con Django. Permite gestionar productos, clientes, empleados y mucho más.

## 🚀 Instalación y ejecución

Sigue estos pasos para ejecutar el proyecto en tu computador:

### 1. Clona el repositorio

```bash
git clone https://github.com/TU_USUARIO/Ferremax.git
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

### 4. Aplica las migraciones para crear la base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. (Opcional) Crea un superusuario para acceder al panel de administración

```bash
python manage.py createsuperuser
```

### 6. Ejecuta el servidor de desarrollo

```bash
python manage.py runserver
```

### 7. Accede a la aplicación

Abre tu navegador y visita:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📁 Estructura del proyecto

- `Ferremax/` - Configuración principal del proyecto Django
- `appFerremax/` - Aplicación principal (modelos, vistas, templates, etc.)
- `requirements.txt` - Dependencias del proyecto

## ⚠️ Notas importantes

- **No subas el archivo `db.sqlite3`** al repositorio. Cada usuario debe crear su propia base de datos ejecutando las migraciones.
- Si necesitas datos de ejemplo, puedes agregarlos desde el panel de administración: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Si usas archivos estáticos personalizados, ejecuta:
  ```bash
  python manage.py collectstatic
  ```

## 📞 Soporte

¿Dudas o problemas? Contacta al equipo de desarrollo o abre un issue en este repositorio.

---

¡Gracias por usar Ferremax! 🛒🔧
