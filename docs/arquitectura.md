# Arquitectura del proyecto

## 1. Visión general

Este proyecto es una aplicación web ligera para gestionar clientes con Flask. Su propósito es permitir registrar, consultar, editar y eliminar información de clientes en un archivo JSON, con una interfaz HTML simple generada por Jinja2.

La solución está pensada como una aplicación monolítica pequeña, con capas bien diferenciadas entre presentación, lógica de negocio y persistencia.

## 2. Objetivos del sistema

- Administrar información de clientes con operaciones CRUD.
- Permitir búsqueda por nombre, email, teléfono o empresa.
- Mantener la aplicación simple, clara y fácil de ejecutar localmente.
- Facilitar pruebas automatizadas del comportamiento principal.

## 3. Componentes principales

### 3.1. Aplicación Flask

El punto de entrada es `app.py`.

Responsabilidades:
- crear la instancia de Flask
- configurar la persistencia JSON
- definir el modelo de datos
- registrar las rutas HTTP
- gestionar mensajes flash y redirecciones

La aplicación se ejecuta con:

```bash
python app.py
```

### 3.2. Modelo de dominio

La entidad principal es `Cliente`, definida en `app.py`.

Campos principales:
- `id`: identificador único
- `nombre`: nombre del cliente
- `email`: correo electrónico único
- `telefono`: teléfono de contacto
- `empresa`: empresa opcional
- `creado_en`: timestamp de creación

La entidad es un dataclass de Python. Los registros se serializan como objetos JSON, con `creado_en` en formato ISO 8601.

### 3.3. Persistencia

La capa de persistencia usa un archivo JSON configurable mediante `CLIENTES_JSON_PATH`.

Por defecto, el archivo local es `instance/clientes.json`. En Azure se guarda en `/home/data/clientes.json`, fuera del paquete publicado, para mantener los datos entre despliegues. Si aún no existe, se inicializa con `test/fixtures/clientes.json`.

Las escrituras generan primero un archivo temporal en el mismo directorio y lo sustituyen de forma atómica para evitar dejar JSON parcialmente escrito. Este almacenamiento está pensado para una aplicación pequeña y no coordina escrituras concurrentes entre procesos.

### 3.4. Vistas y templates

La capa de presentación está separada en la carpeta `templates/`:

- `base.html`: estructura base del HTML
- `index.html`: listado de clientes y búsqueda
- `form.html`: formulario para crear y editar clientes

Los templates renderizan datos dinámicos con Jinja2 y reciben información desde las rutas Flask.

### 3.5. Recursos estáticos

En `static/` se encuentran los archivos CSS para el estilo visual de la interfaz.

## 4. Flujo de funcionamiento

### 4.1. Listado de clientes

Cuando el usuario accede a `/`:
1. La ruta `listar_clientes()` lee el parámetro `q` de la query string.
2. Si hay un término de búsqueda, filtra los registros JSON sin distinguir mayúsculas en nombre, email, teléfono y empresa.
3. Ordena los clientes por ID descendente.
4. Renderiza la vista `index.html` con el listado resultante.

### 4.2. Creación de clientes

Cuando se envía el formulario de `/clientes/nuevo`:
1. Se valida que nombre, email y teléfono no estén vacíos.
2. Se normaliza el email a minúsculas.
3. Se crea una instancia de `Cliente`.
4. Se añade a la lista cargada desde JSON y se escribe el archivo de forma atómica.
5. Si el email ya existe, se informa al usuario y no se modifica el archivo.

### 4.3. Edición de clientes

Cuando se envía el formulario de `/clientes/<id>/editar`:
1. Se localiza el cliente por su ID.
2. Si no existe, la ruta responde con `404`.
3. Se validan los datos del formulario.
4. Se actualizan los atributos del objeto.
5. Se persiste la lista actualizada en el archivo JSON.

### 4.4. Eliminación de clientes

La ruta `/clientes/<id>/eliminar`:
1. Busca el cliente por ID.
2. Si existe, lo elimina de la lista y persiste el archivo JSON.
3. Redirige al listado principal.

## 5. Patrones de diseño aplicados

### Monolito simple

La aplicación no usa una arquitectura distribuida ni microservicios. Todo está contenido en un único proyecto Python con Flask.

### Separación simple de responsabilidades

- `app.py`: lógica principal y rutas
- `templates/`: interfaz de usuario
- `static/`: estilos
- `test/`: pruebas automatizadas

### Modelo MVC ligero

Aunque no es un framework MVC completo, la app sigue una estructura muy cercana a:
- Modelo: `Cliente`
- Vista: templates Jinja2
- Controlador: rutas Flask

## 6. Seguridad y validaciones

La aplicación implementa validaciones básicas:
- requisitos de nombre, email y teléfono
- email único para cada cliente
- uso de `flash()` para comunicar errores y confirmaciones al usuario

La clave secreta de la app se configura mediante `SECRET_KEY`, aunque en un entorno de producción debería sustituirse por un valor real y seguro.

## 7. Pruebas

El proyecto incluye pruebas automatizadas en `test/test.py` usando pytest. Cubren:
- creación exitosa de clientes
- validación de campos obligatorios
- email duplicado
- edición
- eliminación
- búsqueda por texto

Esto permite validar el comportamiento principal sin necesidad de interactuar manualmente con la interfaz.

## 8. Decisiones de arquitectura

- Se eligió Flask por su simplicidad y rapidez en la construcción de aplicaciones pequeñas.
- JSON se usa como persistencia simple para una aplicación pequeña y para facilitar datos de prueba reproducibles.
- El archivo se configura por entorno para separar el almacenamiento persistente del paquete desplegado en Azure.
- El proyecto prioriza legibilidad y operación directa frente a una arquitectura más compleja.

## 9. Evolución recomendada

Si el proyecto crece, las mejoras más naturales serían:
- separar lógica en blueprints
- crear una capa de servicios
- mover validaciones a formularios o schemas
- usar PostgreSQL en lugar de SQLite para producción
- añadir autenticación para administradores

## 10. Resumen

La arquitectura actual es un monolito Flask con persistencia JSON y una capa de presentación en templates. Es adecuada para una aplicación pequeña o pruebas automatizadas, y conserva una ejecución simple y mantenible.
