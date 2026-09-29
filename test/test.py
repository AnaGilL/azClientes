import pytest

from app import Cliente, app, db


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def crear_cliente(client, nombre="Ana Gómez", email="ana@test.com", telefono="5551234", empresa="Acme"):
    return client.post(
        "/clientes/nuevo",
        data={
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "empresa": empresa,
        },
        follow_redirects=True,
    )


def test_index_lista_clientes_vacia(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Gestion de clientes" in response.data
    assert b"No hay clientes registrados todavia." in response.data


def test_crear_cliente_con_datos_validos(client):
    response = crear_cliente(client)

    assert response.status_code == 200
    assert b"Cliente creado correctamente." in response.data
    assert Cliente.query.count() == 1
    cliente = Cliente.query.first()
    assert cliente.nombre == "Ana Gómez"
    assert cliente.email == "ana@test.com"


def test_crear_cliente_rechaza_campos_obligatorios(client):
    response = client.post(
        "/clientes/nuevo",
        data={
            "nombre": "",
            "email": "",
            "telefono": "",
            "empresa": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Nombre, email y telefono son obligatorios." in response.data
    assert Cliente.query.count() == 0


def test_crear_cliente_rechaza_email_duplicado(client):
    crear_cliente(client)

    response = crear_cliente(client, email="ana@test.com", nombre="Ana Segunda")

    assert response.status_code == 200
    assert b"El email ya existe. Usa uno diferente." in response.data
    assert Cliente.query.count() == 1


def test_editar_cliente_actualiza_datos(client):
    crear_cliente(client)

    response = client.post(
        "/clientes/1/editar",
        data={
            "nombre": "Ana Editada",
            "email": "ana.nueva@test.com",
            "telefono": "9998887",
            "empresa": "Nueva Empresa",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Cliente actualizado correctamente." in response.data
    cliente = db.session.get(Cliente, 1)
    assert cliente.nombre == "Ana Editada"
    assert cliente.email == "ana.nueva@test.com"


def test_eliminar_cliente(client):
    crear_cliente(client)

    response = client.post("/clientes/1/eliminar", follow_redirects=True)

    assert response.status_code == 200
    assert b"Cliente eliminado correctamente." in response.data
    assert Cliente.query.count() == 0


def test_buscar_por_nombre_email_telefono_y_empresa(client):
    crear_cliente(client, nombre="Juan Pérez", email="juan@empresa.com", telefono="123456", empresa="Tech")
    crear_cliente(client, nombre="Ana López", email="ana@otros.com", telefono="987654", empresa="Consultora")

    response = client.get("/?q=tech")
    assert response.status_code == 200
    assert b"Juan P\xc3\xa9rez" in response.data
    assert b"Ana L\xc3\xb3pez" not in response.data

    response = client.get("/?q=ana@otros.com")
    assert b"Ana L\xc3\xb3pez" in response.data
