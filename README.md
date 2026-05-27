# 🍺 PERUVIAM Quality Management System (PQMS)

Sistema web de control de calidad industrial para la cervecería **PERUVIAM**.
Permite registrar la producción, calcular automáticamente estadísticas, generar
gráficas de control, gestionar documentación ISO 9000, capacitación, reclamos,
reportes y trazabilidad de lotes.

## 🛠️ Tecnologías

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend:** Python 3.10+, Flask
- **Estadística:** Pandas, NumPy
- **Visualización:** Plotly, Matplotlib
- **Base de datos:** MySQL (vía SQLAlchemy + PyMySQL)

## 📁 Estructura del proyecto

```
pqms/
├── run.py                 # Punto de entrada
├── config.py              # Configuración
├── requirements.txt
├── .env.example
├── database/schema.sql
└── app/
    ├── __init__.py        # App factory
    ├── models/            # Modelos SQLAlchemy
    ├── routes/            # Blueprints / controladores
    ├── services/          # Lógica de negocio (estadística, auditoría)
    ├── middlewares/       # RBAC y decoradores
    ├── templates/         # HTML Jinja2
    └── static/            # CSS, JS, uploads
```

## 🚀 Instalación local

### 1. Clonar y entrar al proyecto

```bash
cd pqms
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de MySQL:

```
SECRET_KEY=tu_clave_secreta
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pqms_db
```

### 5. Crear la base de datos en MySQL

```bash
mysql -u root -p < database/schema.sql
```

(o simplemente en MySQL: `CREATE DATABASE pqms_db;`)

### 6. Ejecutar la aplicación

```bash
python run.py
```

Abre tu navegador en: **http://localhost:5000**

Las tablas y los datos de ejemplo (usuarios y cursos) se crean automáticamente.

## 👥 Cuentas demo

| Rol         | Usuario     | Contraseña |
|-------------|-------------|------------|
| Administrador | `admin`     | `admin123` |
| Supervisor    | `supervisor`| `super123` |
| Operario      | `operario`  | `oper123`  |

## 📦 Módulos del sistema

1. **Login y RBAC** — sesión por rol (admin / supervisor / operario) + bitácora.
2. **Registro de Producción** — lotes, evidencias, tabla de frecuencias / desviaciones.
3. **Control Estadístico** — medidas, histograma, gráficas X / Pareto / Ishikawa, alertas.
4. **ISO 9000** — documentos, auditorías, no conformidades, acciones correctivas.
5. **Capacitación** — cursos, inscripciones, seguimiento, evaluaciones.
6. **Dashboard** — KPIs en tiempo real con filtros.
7. **Reclamos** — registro y seguimiento por lote.
8. **Reportes** — exportación a Excel y PDF.
9. **Trazabilidad** — Lote → Operario → Fecha → Calidad → Reclamos.

## 🔐 Seguridad

- Contraseñas hasheadas con Werkzeug (PBKDF2).
- Decoradores RBAC en cada endpoint sensible.
- Sesiones gestionadas con Flask-Login.
- Subida de archivos con `secure_filename` + UUID.
- Bitácora de auditoría de todas las acciones críticas.

## 📝 Notas

- Carpeta de uploads: `app/static/uploads/` (se crea automáticamente).
- Para producción: usar `gunicorn` o `waitress` y configurar `FLASK_ENV=production`.
- La aplicación es responsive (Bootstrap 5).
