Documentación de endpoints — azClientes
Aplicación web CRUD de clientes construida con Flask 3.1.0 + Flask-SQLAlchemy 3.1.1 sobre SQLite (sqlite:///clientes.db).

Nota importante sobre el tipo de API app.py no expone una API REST/JSON. Todas las rutas son endpoints web (server-side rendering): reciben datos por application/x-www-form-urlencoded o por query string y responden con HTML (Jinja2) o con una redirección HTTP 302. Este documento describe esas rutas tal como están implementadas.

Base URL (desarrollo): http://127.0.0.1:5000
Autenticación: ninguna (la aplicación no implementa login ni control de acceso).
Formato de respuesta: text/html, salvo las redirecciones.
Modelo de datos: Cliente
Tabla generada automáticamente con db.create_all() al arrancar app.py.

Campo	Tipo	Restricciones	Descripción
id	Integer	Clave primaria, autoincremental	Identificador del cliente
nombre	String(120)	nullable=False	Nombre del cliente (obligatorio)
email	String(120)	unique=True, nullable=False	Correo electrónico; debe ser único
telefono	String(30)	nullable=False	Teléfono de contacto (obligatorio)
empresa	String(120)	nullable=True	Empresa asociada (opcional)
creado_en	DateTime	nullable=False, default datetime.utcnow	Fecha/hora de alta en UTC
Resumen de endpoints
Método	Ruta	Función (url_for)	Operación CRUD
GET	/	listar_clientes	Read / búsqueda
GET	/clientes/nuevo	crear_cliente	Formulario de alta
POST	/clientes/nuevo	crear_cliente	Create
GET	/clientes/<int:cliente_id>/editar	editar_cliente	Formulario de edición
POST	/clientes/<int:cliente_id>/editar	editar_cliente	Update
POST	/clientes/<int:cliente_id>/eliminar	eliminar_cliente	Delete
1. Listar y buscar clientes
GET /
Devuelve index.html con todos los clientes ordenados por id descendente (order_by(Cliente.id.desc())), es decir, el más reciente primero.

Parámetros (query string)
Parámetro	Tipo	Obligatorio	Descripción
q	string	No	Término de búsqueda. Se aplica con ILIKE '%q%' de forma combinada (OR) sobre nombre, email, telefono y empresa. Si se omite o va vacío, se devuelve la lista completa.
Respuestas
Código	Contenido
200 OK	HTML con la tabla de clientes. Si no hay registros, muestra "No hay clientes registrados todavia."
Ejemplos
# Lista completa
curl "http://127.0.0.1:5000/"

# Búsqueda por término
curl "http://127.0.0.1:5000/?q=contoso"
2. Mostrar formulario de alta
GET /clientes/nuevo
Devuelve form.html con el título "Nuevo cliente" y el formulario vacío (cliente=None).

Código	Contenido
200 OK	HTML del formulario de creación
3. Crear cliente
POST /clientes/nuevo
Content-Type: application/x-www-form-urlencoded
Cuerpo del formulario
Campo	Tipo	Obligatorio	Normalización aplicada
nombre	string	Sí	.strip()
email	string	Sí	.strip().lower()
telefono	string	Sí	.strip()
empresa	string	No	.strip(); si queda vacío se guarda como NULL
Respuestas
Código	Situación	Comportamiento
302 Found → /	Alta correcta	Mensaje flash success: "Cliente creado correctamente."
200 OK	Falta nombre, email o telefono	Se vuelve a renderizar el formulario con flash error: "Nombre, email y telefono son obligatorios."
200 OK	Email duplicado (IntegrityError)	rollback() y flash error: "El email ya existe. Usa uno diferente."
Ejemplo
curl -X POST "http://127.0.0.1:5000/clientes/nuevo" \
  -d "nombre=Ana Gil" \
  -d "email=ana@contoso.com" \
  -d "telefono=5555551234" \
  -d "empresa=Contoso"
4. Mostrar formulario de edición
GET /clientes/<int:cliente_id>/editar
Recupera el cliente con Cliente.query.get_or_404(cliente_id) y devuelve form.html con el título "Editar cliente" y los campos precargados.

Parámetro de ruta	Tipo	Descripción
cliente_id	integer	ID del cliente a editar
Código	Situación
200 OK	Formulario con los datos actuales
404 Not Found	No existe un cliente con ese id
5. Actualizar cliente
POST /clientes/<int:cliente_id>/editar
Content-Type: application/x-www-form-urlencoded
Mismos campos y misma normalización que el alta (nombre, email, telefono, empresa).

Respuestas
Código	Situación	Comportamiento
302 Found → /	Actualización correcta	Flash success: "Cliente actualizado correctamente."
200 OK	Falta un campo obligatorio	Se re-renderiza el formulario con flash error: "Nombre, email y telefono son obligatorios."
200 OK	Email duplicado (IntegrityError)	rollback() y flash error: "El email ya existe. Usa uno diferente."
404 Not Found	El cliente_id no existe	—
Ejemplo
curl -X POST "http://127.0.0.1:5000/clientes/3/editar" \
  -d "nombre=Ana Gil Lara" \
  -d "email=ana.gil@contoso.com" \
  -d "telefono=5555559999" \
  -d "empresa=Contoso México"
6. Eliminar cliente
POST /clientes/<int:cliente_id>/eliminar
Solo acepta POST (desde el formulario de la tabla, con confirmación JavaScript). No recibe cuerpo.

Código	Situación	Comportamiento
302 Found → /	Eliminación correcta	Flash success: "Cliente eliminado correctamente."
404 Not Found	El cliente_id no existe	—
405 Method Not Allowed	Se intenta con GET	—
Ejemplo
curl -X POST "http://127.0.0.1:5000/clientes/3/eliminar"
Mensajes flash
Todas las operaciones de escritura usan flash(mensaje, categoria) y se renderizan en base.html.

Categoría	Mensaje
success	Cliente creado correctamente.
success	Cliente actualizado correctamente.
success	Cliente eliminado correctamente.
error	Nombre, email y telefono son obligatorios.
error	El email ya existe. Usa uno diferente.
Códigos de estado utilizados
Código	Cuándo se produce
200 OK	Renderizado de listado o formulario (incluye re-render por error de validación)
302 Found	Redirección a / tras crear, actualizar o eliminar
404 Not Found	get_or_404() cuando el cliente_id no existe
405 Method Not Allowed	Método HTTP no permitido en la ruta (p. ej. GET en /eliminar)
Consideraciones antes de exponer la aplicación
Observaciones derivadas del código actual de app.py:

SECRET_KEY embebida en el código ("cambia-esta-clave-secreta"). Debe leerse de una variable de entorno antes de cualquier despliegue.
app.run(debug=True): el modo debug expone el depurador interactivo de Werkzeug; no debe usarse fuera de desarrollo local.
Sin servidor WSGI de producción: requirements.txt solo declara Flask y Flask-SQLAlchemy; para desplegar haría falta añadir, por ejemplo, gunicorn o waitress.
Sin autenticación ni CSRF: los formularios de escritura (crear, editar, eliminar) no llevan token CSRF ni control de acceso.
Sin validación de formato de email más allá del type="email" del navegador: una petición directa (curl/Postman) puede insertar cualquier cadena.
SQLite local: clientes.db se crea en instance/ y está en .gitignore; no es adecuado para escenarios multiinstancia.