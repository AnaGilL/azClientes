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
- `test/fixtures/clientes.json`: datos iniciales de prueba
- `instance/clientes.json`: persistencia JSON local (se crea al primer acceso)

## Despliegue en Azure

El workflow de GitHub Actions crea o reutiliza la infraestructura al hacer push a `main`. Antes del primer despliegue, configura en **Settings > Secrets and variables > Actions**:

- Una variable de repositorio `AZURE_WEBAPP_NAME` con un nombre globalmente unico para la URL `<nombre>.azurewebsites.net`.
- Un secreto `AZURE_CREDENTIALS` con las credenciales JSON del service principal usado por `azure/login`. Debe tener el rol `Contributor` en la suscripcion para crear el grupo de recursos.

Se aprovisionan el grupo `grClientes`, un App Service Plan Linux F1, una Web App con Python 3.12, un workspace de Log Analytics y Application Insights en `eastus`. La Web App se inicia con Gunicorn y envía telemetría a Application Insights. Los datos JSON se guardan en `/home/data/clientes.json`, fuera del paquete desplegado, para conservarlos entre despliegues. El archivo `test/fixtures/clientes.json` se copia a esa ubicación la primera vez que no exista un archivo de datos.

El almacenamiento JSON está pensado para una aplicación pequeña o pruebas; no coordina escrituras simultáneas entre varios procesos. F1 tiene límites de uso; la disponibilidad del SKU depende de la suscripción y la región, y la ingesta de telemetría puede generar cargos si supera las cuotas gratuitas.
