# 🛠️ Ferremax

Ferremax es una aplicación web de ferretería desarrollada con Django y SQLite. Permite gestionar productos, clientes, empleados, pedidos y mucho más. La aplicación incluye una API REST construida con FastAPI para acceder a los datos de empleados y productos, junto con funcionalidad de filtrado interactivo para la visualización de productos y pedidos.

## 🚀 Instalación y ejecución

Sigue estos pasos para ejecutar el proyecto en tu computador o presentarlo en cualquier PC:

### 1. Clona el repositorio o descarga el ZIP

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
Esto creará todas las tablas y cargará automáticamente:
- Comunas y regiones de Chile
- Cargos de empleados
- Productos iniciales con imágenes de ejemplo
- Empleados de demostración
- Cliente por defecto (si no existen clientes)
- Producto por defecto (si no existen productos)

### 5. Crea el superusuario predefinido para acceso administrativo

```bash
python manage.py crear_superusuario
```
Este comando crea un superusuario para ingresar al panel de admin de django

O en Windows, simplemente ejecuta:
```bash
crear_superuser.bat
```

### 6. Ejecuta el servidor de desarrollo Django

```bash
python manage.py runserver
```

### 7. Accede a la aplicación principal

Accede a la aplicación web desde tu navegador en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 8. Inicia la API FastAPI (en otra terminal)

Para iniciar la API de FastAPI que muestra la información de empleados y productos, abre otra terminal, activa el entorno virtual si es necesario y ejecuta:

```bash
# Inicia la API en puerto 8001
python appFerremax/fastapi_app.py
```

O en Windows, simplemente ejecuta:
```bash
run_fastapi.bat
```

> **Nota importante:** La API de FastAPI debe estar corriendo para que funcionen correctamente las vistas de productos API (productosapi) y la vista de empleados basada en API.

## 📚 Estructura de la aplicación

### Aplicación web principal (Django - Puerto 8000)

- **Panel de administración**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Página principal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Productos (con filtro)**: [http://127.0.0.1:8000/productos/](http://127.0.0.1:8000/productos/)
- **Carrito de compras**: [http://127.0.0.1:8000/carrito/](http://127.0.0.1:8000/carrito/)
- **Mis pedidos** (requiere inicio de sesión): [http://127.0.0.1:8000/mispedidos/](http://127.0.0.1:8000/mispedidos/)
- **Ver pedidos** (admin): [http://127.0.0.1:8000/pedidos/](http://127.0.0.1:8000/pedidos/)

### API REST (FastAPI - Puerto 8001)

Documentación interactiva: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

#### API de Empleados:
- **Lista de empleados**: [http://127.0.0.1:8001/api/empleados/](http://127.0.0.1:8001/api/empleados/)
- **Detalles de un empleado**: [http://127.0.0.1:8001/api/empleados/1](http://127.0.0.1:8001/api/empleados/1) (reemplaza 1 con el ID del empleado)
- **Interfaz web de empleados**: [http://127.0.0.1:8001/empleados-web](http://127.0.0.1:8001/empleados-web)

#### API de Productos:
- **Lista de productos**: [http://127.0.0.1:8001/api/productos/](http://127.0.0.1:8001/api/productos/)
- **Detalles de un producto**: [http://127.0.0.1:8001/api/productos/1](http://127.0.0.1:8001/api/productos/1) (reemplaza 1 con el ID del producto)
- **Interfaz web de productos vía API**: [http://127.0.0.1:8001/productosapi](http://127.0.0.1:8001/productosapi)

## 🌟 Características principales

### Catálogo de productos
- Vista completa de productos con imágenes
- **Filtrado interactivo en tiempo real** en páginas de productos (web y API):
  - Buscar productos por nombre o marca
  - Filtrar por precio máximo usando un control deslizante
  - Mostrar solo productos en stock
  - Reiniciar todos los filtros con un solo clic
- Vista detallada de productos individuales
- Interfaz moderna con Bootstrap 5

### Carrito de compras moderno
- Agregar y eliminar productos
- Actualizar cantidades con controles AJAX en tiempo real
- Ver subtotal y total actualizados dinámicamente
- **Aplicación automática de descuentos** (25% al agregar 4 o más productos)
- **Persistencia del carrito en sesión** (carrito guardado entre visitas)
- **Integración con PayPal** para procesamiento de pagos

### Gestión de pedidos
- Vista de "Mis Pedidos" para clientes (seguimiento de pedidos)
- Página de confirmación detallada después de cada compra
- **Filtrado avanzado de pedidos** para administradores
- Seguimiento de estado de pedidos (En proceso, Enviado, Entregado)

### Panel administrativo
- Gestión completa de productos, clientes y pedidos
- Carga de imágenes para productos
- Vista detallada de pedidos con filtros avanzados
- Estadísticas de ventas

### API REST con FastAPI
- **Documentación interactiva con Swagger UI**
- Endpoints para listar y obtener detalles de empleados y productos
- Vistas web integradas para demostrar el uso de la API
- CORS habilitado para integración con otras aplicaciones
- Manejo correcto de imágenes y archivos estáticos

### Integración de frameworks
- Django para la aplicación principal y ORM
- FastAPI para API REST moderna y asíncrona
- Bootstrap 5 para diseño responsive
- AJAX y Fetch API para actualizaciones dinámicas sin recargar la página

### Seguridad y rendimiento
- Autenticación de usuarios para áreas protegidas
- Validación de formularios
- Protección contra CSRF en formularios Django
- Manejo adecuado de transacciones de base de datos

---

## 🔧 Datos de prueba preconfigurados

El sistema incluye los siguientes datos para pruebas:

### Administrador
- Usuario: admin
- Contraseña: ferremax2025

### Clientes
- Usuario: cliente1
- Contraseña: ferremax123

### Cliente por defecto (creado automáticamente)
- RUT: 11111111-1
- Correo: cliente.demo@ferremax.com
- Contraseña: clientedemo123
- Nombre: Cliente Demo

### Producto por defecto (creado automáticamente)
- Nombre: Martillo profesional
- Descripción: Martillo de carpintero con mango ergonómico y cabeza de acero reforzado
- Marca: Ferremax Tools
- Precio: $12,990
- Stock: 50 unidades

---

## 📞 Soporte

¿Dudas o problemas? Contacta al equipo de desarrollo o abre un issue en este repositorio.

---

¡Gracias por usar Ferremax! 🛒🔧

## 📐 Arquitectura del proyecto

### Diferencia entre vistas web y endpoints API

El proyecto Ferremax utiliza una arquitectura híbrida que combina:

1. **Vistas web tradicionales (Django)**: Generan HTML renderizado en el servidor
2. **APIs REST (Django REST Framework y FastAPI)**: Devuelven datos en formato JSON
3. **Vistas web que consumen APIs (Híbridas)**: Páginas HTML que obtienen datos vía JavaScript

#### Endpoints API (JSON)

Estos endpoints devuelven datos en formato JSON y están diseñados para ser consumidos por aplicaciones frontend o servicios externos:

- **FastAPI** (puerto 8001):
  - `/api/empleados/`: Lista todos los empleados (JSON)
  - `/api/empleados/{id}`: Detalles de un empleado específico (JSON)
  - `/api/productos/`: Lista todos los productos (JSON)
  - `/api/productos/{id}`: Detalles de un producto específico (JSON)

- **Django REST Framework** (puerto 8000):
  - `/api/vendedores/`: API para vendedores (implementada con DRF)

#### Vistas web (HTML)

Estas rutas generan HTML y están diseñadas para ser visitadas directamente por usuarios:

- **Django** (puerto 8000):
  - `/`: Página principal
  - `/productos/`: Catálogo de productos (HTML generado por Django)
  - `/carrito/`: Carrito de compras
  - `/pedidos/`: Administración de pedidos
  - `/admin/`: Panel de administración Django

- **FastAPI** (puerto 8001):
  - `/empleados-web`: Página de empleados que consume la API mediante JavaScript
  - `/productosapi`: Página de productos que consume la API mediante JavaScript

### Flujo de datos

1. **Vistas tradicionales**: El navegador solicita una URL → Django procesa → Devuelve HTML completo
2. **Consumo de API**: El navegador carga HTML básico → JavaScript realiza peticiones fetch → Actualiza el DOM dinámicamente

Esta arquitectura híbrida permite:
- Desarrollo frontend moderno con JavaScript
- SEO mejorado gracias al renderizado en servidor
- Reutilización de lógica entre aplicaciones web y móviles
- Separación clara entre presentación y datos

## 💸 Flujo de compra y pago

### Proceso de compra completo

1. **Selección de productos**:
   - El usuario navega por el catálogo de productos
   - Agrega productos al carrito desde la página de productos o detalles del producto
   - Puede ver y modificar el carrito en cualquier momento

2. **Gestión del carrito**:
   - Ver todos los productos agregados
   - Modificar cantidades con controles + y - (AJAX en tiempo real)
   - Ver subtotales por producto y total general
   - Aplicación automática de descuento del 25% cuando hay 4 o más productos diferentes
   - El carrito se guarda en la sesión del usuario (persiste entre visitas)

3. **Proceso de pago con PayPal**:
   - El usuario hace clic en "Pagar con PayPal"
   - Se abre la ventana de PayPal para completar el pago
   - Tras el pago exitoso, se registra la transacción en la base de datos
   - El usuario es redirigido a una página de confirmación con los detalles del pedido

4. **Confirmación y seguimiento**:
   - Página de confirmación con resumen detallado del pedido
   - El usuario puede acceder a "Mis Pedidos" para ver el historial y estado de sus compras
   - Los administradores pueden ver y gestionar todos los pedidos desde la sección de administración

### Integración con PayPal

La integración con PayPal utiliza el SDK de PayPal para JavaScript y permite:
- Pagos seguros con tarjeta de crédito o cuenta PayPal
- Transacciones en múltiples monedas
- Confirmación inmediata del pago
- Registros detallados de transacciones

> **Nota**: Para pruebas, se puede usar la cuenta sandbox de PayPal:
> - Email: sb-43zfpz30323401@personal.example.com
> - Contraseña: 12345678

## 💰 Sistema de pagos y finanzas

### Vista de contador

Para los usuarios con rol de Contador o Administrador, el sistema proporciona una vista especializada para la gestión financiera:

- **URL**: [http://127.0.0.1:8000/pagos/](http://127.0.0.1:8000/pagos/)
- **Acceso**: Restringido a usuarios con roles "Contador" o "Administrador"

### Características principales:

1. **Registro de transacciones**:
   - Visualización detallada de todas las transacciones de ventas
   - Información de fecha, cliente, producto, cantidad y total en CLP
   - Formateo adecuado de valores monetarios en formato chileno

2. **Registro de pagos**:
   - Seguimiento de todos los pagos procesados
   - Detalles de fecha, pedido, método de pago, estado y monto
   - Integración con datos de pedidos para mostrar información completa

3. **Balance financiero**:
   - Resumen de total de ventas, ingresos y egresos
   - Cálculo automático del balance final
   - Presentación clara con formato profesional

4. **Exportación a PDF**:
   - Generación de reportes financieros en formato PDF
   - Documento formateado profesionalmente con encabezado y pie de página
   - Ideal para impresión o archivado de informes
   - Incluye fecha de generación y datos completos del balance

Para acceder a esta funcionalidad, inicie sesión como administrador o contador y navegue a la sección "Pagos" desde el menú principal o directamente a través de la URL.
