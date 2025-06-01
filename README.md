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

Abre tu navegador y visita:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📞 Soporte

¿Dudas o problemas? Contacta al equipo de desarrollo o abre un issue en este repositorio.

---

¡Gracias por usar Ferremax! 🛒🔧
