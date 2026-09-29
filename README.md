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
