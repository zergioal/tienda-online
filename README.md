# TechStore — Sistema de Tienda Online

**Materia:** Taller de Aplicaciones en Internet  
**Universidad:** Universidad Adventista de Bolivia  
**Autor:** Sergio Mauricio Alcocer Valenzuela

---

## Descripción

TechStore es un sistema web de venta de accesorios de computadoras y servicio técnico, desarrollado con Flask y Flask-AppBuilder. Permite gestionar productos, clientes, órdenes de compra y servicios técnicos, con roles diferenciados por tipo de usuario e integración de Inteligencia Artificial para pronósticos de negocio.

---

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje principal |
| Flask | Framework web |
| Flask-AppBuilder | Scaffolding, auth, roles, CRUD |
| SQLAlchemy + SQLite | Base de datos ORM |
| Chart.js | Gráficas en reportes |
| Google Gemini 2.5 Flash | Pronósticos con IA |
| python-dotenv | Gestión de variables de entorno |
| Bootstrap 3 | Interfaz de usuario |

---

## Estructura de la base de datos

El sistema cuenta con **6 tablas** y **5 relaciones** (claves foráneas):

```
Categoria ──< Producto ──< DetalleOrden >── Orden >── Cliente
                                                          │
                                                          └──< ServicioTecnico
```

| Tabla | Descripción |
|---|---|
| `Categoria` | Clasificación de productos |
| `Producto` | Accesorios de computadoras con precio y stock |
| `Cliente` | Datos del comprador |
| `Orden` | Cabecera de cada compra |
| `DetalleOrden` | Líneas de producto por orden (tabla intermedia) |
| `ServicioTecnico` | Registro de reparaciones y diagnósticos |

---

## Roles y permisos

| Rol | Acceso |
|---|---|
| **Admin** | Acceso total al sistema |
| **Supervisor** | Gestiona servicios técnicos, visualiza órdenes/clientes y accede a todos los reportes |
| **Usuario** | Solo ve el catálogo de productos, puede agregar al carrito y realizar compras |

Credenciales de demo:

| Usuario | Contraseña |
|---|---|
| admin | admin123 |
| supervisor | supervisor123 |
| usuario | user123 |

---

## Funcionalidades principales

### Catálogo y Tienda (rol Usuario)
- Catálogo de productos con filtro por categoría
- Carrito de compras en sesión
- Checkout con registro automático de cliente y orden
- Confirmación de compra con detalle

### Gestión (rol Admin / Supervisor)
- CRUD completo de Categorías, Productos, Clientes
- Registro de Órdenes con múltiples productos
- Gestión de Servicios Técnicos (ingreso, diagnóstico, estado, entrega)

### Reportes con gráficas (rol Supervisor / Admin)
1. **Ventas por Mes** — Gráfica de barras con historial mensual
2. **Productos más Vendidos** — Top 10 por unidades vendidas
3. **Servicios Técnicos por Estado** — Gráfica de dona (Pendiente / En Proceso / Listo / Entregado)

### Inteligencia Artificial (Google Gemini)
Cada reporte incluye un panel con **3 pronósticos generados automáticamente** por Gemini 2.5 Flash:
- Pronósticos de ventas para los próximos meses
- Recomendaciones de inventario según productos más vendidos
- Pronósticos operacionales del servicio técnico

---

## Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd tienda-online
```

### 2. Crear entorno virtual e instalar dependencias
```bash
py -3 -m venv venv
venv\Scripts\activate        # Windows
pip install flask flask-appbuilder flask-sqlalchemy python-dotenv google-genai
```

### 3. Configurar API key de Gemini (opcional)
```bash
# Copiar el archivo de ejemplo
copy .env.example .env
# Editar .env y agregar tu key de https://aistudio.google.com/apikey
```

### 4. Cargar datos de demo
```bash
python seed_data.py
```

### 5. Ejecutar el servidor
```bash
python run.py
```

Acceder en: [http://localhost:5000](http://localhost:5000)

---

## Estructura del proyecto

```
tienda-online/
├── app/
│   ├── __init__.py          # Fábrica de la app, roles y permisos
│   ├── models.py            # Modelos SQLAlchemy (6 tablas)
│   ├── views.py             # Vistas: dashboard, catálogo, órdenes, reportes
│   ├── ai_service.py        # Integración con Google Gemini
│   ├── static/css/
│   │   └── custom.css       # Estilos personalizados
│   └── templates/
│       ├── landing.html     # Página pública de inicio
│       ├── index.html       # Dashboard Admin/Supervisor
│       ├── catalogo/        # Plantillas de tienda
│       └── reports/         # Plantillas de reportes con IA
├── config.py                # Configuración Flask
├── run.py                   # Punto de entrada
├── seed_data.py             # Datos de demo
├── diagrama_er.html         # Diagrama entidad-relación interactivo
├── .env.example             # Plantilla de variables de entorno
└── README.md
```

---

## Control de versiones

El proyecto usa **Git** con la siguiente estrategia de ramas:

- `master` — rama principal estable
- `develop` — integración de funcionalidades
- `feature/sergio-models` — desarrollo de modelos y vistas

---

## Diagrama ER

El archivo `diagrama_er.html` contiene un diagrama visual interactivo de la base de datos con las 6 tablas, claves primarias (PK), claves foráneas (FK) y todas las relaciones 1:N.

---

*Proyecto desarrollado para el 2do Parcial — Taller de Aplicaciones en Internet*  
*Universidad Adventista de Bolivia — 2026*
