from datetime import datetime, timezone

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clientes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "cambia-esta-clave-secreta"

db = SQLAlchemy(app)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    empresa = db.Column(db.String(120), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Cliente {self.nombre}>"


@app.route("/")
def listar_clientes():
    termino = request.args.get("q", "").strip()
    consulta = Cliente.query

    if termino:
        patron = f"%{termino}%"
        consulta = consulta.filter(
            or_(
                Cliente.nombre.ilike(patron),
                Cliente.email.ilike(patron),
                Cliente.telefono.ilike(patron),
                Cliente.empresa.ilike(patron),
            )
        )

    clientes = consulta.order_by(Cliente.id.desc()).all()
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

        nuevo_cliente = Cliente(
            nombre=nombre,
            email=email,
            telefono=telefono,
            empresa=empresa,
        )

        db.session.add(nuevo_cliente)
        try:
            db.session.commit()
            flash("Cliente creado correctamente.", "success")
            return redirect(url_for("listar_clientes"))
        except IntegrityError:
            db.session.rollback()
            flash("El email ya existe. Usa uno diferente.", "error")

    return render_template("form.html", titulo="Nuevo cliente", cliente=None)


@app.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar_cliente(cliente_id: int):
    cliente = db.session.get(Cliente, cliente_id)
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

        cliente.nombre = nombre
        cliente.email = email
        cliente.telefono = telefono
        cliente.empresa = empresa

        try:
            db.session.commit()
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("listar_clientes"))
        except IntegrityError:
            db.session.rollback()
            flash("El email ya existe. Usa uno diferente.", "error")

    return render_template("form.html", titulo="Editar cliente", cliente=cliente)


@app.route("/clientes/<int:cliente_id>/eliminar", methods=["POST"])
def eliminar_cliente(cliente_id: int):
    cliente = db.session.get(Cliente, cliente_id)
    if cliente is None:
        abort(404)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado correctamente.", "success")
    return redirect(url_for("listar_clientes"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
