# App CRUD de Clientes (Python + Flask)

Aplicacion web para administrar clientes con operaciones CRUD:
- Crear cliente
- Listar clientes
- Editar cliente
- Eliminar cliente
- Buscar por nombre, email, telefono o empresa

## Requisitos
- Python 3.10 o superior

## Instalacion y ejecucion
1. Crear entorno virtual:
   ```powershell
   python -m venv .venv
   ```
2. Activar entorno virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
4. Ejecutar la app:
   ```powershell
   python app.py
   ```
5. Abrir en navegador:
   ```
   http://127.0.0.1:5000
   ```

## Estructura
- `app.py`: aplicacion Flask y rutas CRUD
- `templates/`: vistas HTML con Jinja2
- `static/styles.css`: estilos
- `clientes.db`: base de datos SQLite (se crea automaticamente)

## Despliegue en Azure

El workflow de GitHub Actions crea o reutiliza la infraestructura al hacer push a `main`. Antes del primer despliegue, configura en **Settings > Secrets and variables > Actions**:

- Una variable de repositorio `AZURE_WEBAPP_NAME` con un nombre globalmente unico para la URL `<nombre>.azurewebsites.net`.
- Un secreto `AZURE_CREDENTIALS` con las credenciales JSON del service principal usado por `azure/login`. Debe tener el rol `Contributor` en la suscripcion para crear el grupo de recursos.

Se aprovisionan el grupo `grClientes`, un App Service Plan Linux F1, una Web App con Python 3.12, un workspace de Log Analytics y Application Insights en `eastus`. La Web App se inicia con Gunicorn y envía telemetría a Application Insights. F1 tiene límites de uso; la disponibilidad del SKU depende de la suscripción y la región, y la ingesta de telemetría puede generar cargos si supera las cuotas gratuitas.
