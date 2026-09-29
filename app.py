import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor()

from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["CLIENTES_JSON_PATH"] = os.environ.get(
    "CLIENTES_JSON_PATH", str(Path(app.instance_path) / "clientes.json")
)
app.config["SECRET_KEY"] = "cambia-esta-clave-secreta"


@dataclass
class Cliente:
    id: int
    nombre: str
    email: str
    telefono: str
    empresa: str | None
    creado_en: datetime

    def __repr__(self) -> str:
        return f"<Cliente {self.nombre}>"


def _escribir_json(path: Path, registros: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as archivo:
            temporal = Path(archivo.name)
            json.dump(registros, archivo, ensure_ascii=False, indent=2)
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, path)
    finally:
        if temporal and temporal.exists():
            temporal.unlink()


def _cargar_clientes() -> list[Cliente]:
    path = Path(app.config["CLIENTES_JSON_PATH"])
    if not path.exists():
        semilla = Path(__file__).parent / "test" / "fixtures" / "clientes.json"
        registros = json.loads(semilla.read_text(encoding="utf-8"))
        _escribir_json(path, registros)

    registros = json.loads(path.read_text(encoding="utf-8"))
    return [
        Cliente(
            id=registro["id"],
            nombre=registro["nombre"],
            email=registro["email"],
            telefono=registro["telefono"],
            empresa=registro.get("empresa"),
            creado_en=datetime.fromisoformat(registro["creado_en"]),
        )
        for registro in registros
    ]


def _guardar_clientes(clientes: list[Cliente]) -> None:
    registros = [
        {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": cliente.email,
            "telefono": cliente.telefono,
            "empresa": cliente.empresa,
            "creado_en": cliente.creado_en.isoformat(),
        }
        for cliente in clientes
    ]
    _escribir_json(Path(app.config["CLIENTES_JSON_PATH"]), registros)


def _siguiente_id(clientes: list[Cliente]) -> int:
    return max((cliente.id for cliente in clientes), default=0) + 1


@app.route("/")
def listar_clientes():
    termino = request.args.get("q", "").strip()
    clientes = _cargar_clientes()
    if termino:
        termino = termino.casefold()
        clientes = [
            cliente
            for cliente in clientes
            if any(
                termino in valor.casefold()
                for valor in (
                    cliente.nombre,
                    cliente.email,
                    cliente.telefono,
                    cliente.empresa or "",
                )
            )
        ]
    clientes.sort(key=lambda cliente: cliente.id, reverse=True)
    return render_template("index.html", clientes=clientes, termino=termino)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def crear_cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        empresa = request.form.get("empresa", "").strip() or None

        if not nombre or not email or not telefono:
            flash("Nombre, email y telefono son obligatorios.", "error")
            return render_template("form.html", titulo="Nuevo cliente", cliente=None)

        clientes = _cargar_clientes()
        if any(cliente.email == email for cliente in clientes):
            flash("El email ya existe. Usa uno diferente.", "error")
            return render_template("form.html", titulo="Nuevo cliente", cliente=None)

        clientes.append(
            Cliente(
                id=_siguiente_id(clientes),
                nombre=nombre,
                email=email,
                telefono=telefono,
                empresa=empresa,
                creado_en=datetime.now(timezone.utc),
            )
        )
        _guardar_clientes(clientes)
        flash("Cliente creado correctamente.", "success")
        return redirect(url_for("listar_clientes"))

    return render_template("form.html", titulo="Nuevo cliente", cliente=None)


@app.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar_cliente(cliente_id: int):
    clientes = _cargar_clientes()
    cliente = next((item for item in clientes if item.id == cliente_id), None)
    if cliente is None:
        abort(404)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        empresa = request.form.get("empresa", "").strip() or None

        if not nombre or not email or not telefono:
            flash("Nombre, email y telefono son obligatorios.", "error")
            return render_template("form.html", titulo="Editar cliente", cliente=cliente)

        if any(
            item.id != cliente_id and item.email == email for item in clientes
        ):
            flash("El email ya existe. Usa uno diferente.", "error")
            return render_template("form.html", titulo="Editar cliente", cliente=cliente)

        cliente.nombre = nombre
        cliente.email = email
        cliente.telefono = telefono
        cliente.empresa = empresa
        _guardar_clientes(clientes)
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("listar_clientes"))

    return render_template("form.html", titulo="Editar cliente", cliente=cliente)


@app.route("/clientes/<int:cliente_id>/eliminar", methods=["POST"])
def eliminar_cliente(cliente_id: int):
    clientes = _cargar_clientes()
    restantes = [cliente for cliente in clientes if cliente.id != cliente_id]
    if len(restantes) == len(clientes):
        abort(404)
    _guardar_clientes(restantes)
    flash("Cliente eliminado correctamente.", "success")
    return redirect(url_for("listar_clientes"))


if __name__ == "__main__":
    app.run(debug=True)
