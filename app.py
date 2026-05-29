"""Organiz — organizador de ingresos y gastos (Fase 1).

App Flask que sirve el panel y expone una pequeña API JSON que el frontend
consume con fetch(). Mantener la lógica de datos en models.py y la web aquí
deja el camino libre para la Fase 2 (proyectos y avances): bastará con añadir
nuevos modelos y rutas sin reescribir lo actual.
"""

from flask import Flask, jsonify, render_template, request

import models
from database import init_db

app = Flask(__name__)

# Crea las tablas y siembra categorías al importar el módulo, de modo que la
# app funcione tanto con `flask run` como con `python app.py`.
init_db()


# --------------------------------------------------------------------------- #
# Páginas
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    """Panel principal: resumen y formulario para añadir movimientos."""
    return render_template("index.html")


# --------------------------------------------------------------------------- #
# API JSON
# --------------------------------------------------------------------------- #
@app.get("/api/summary")
def api_summary():
    return jsonify(models.get_summary())


@app.get("/api/transactions")
def api_list_transactions():
    kind = request.args.get("kind")  # opcional: 'income' o 'expense'
    return jsonify(models.list_transactions(kind=kind))


@app.post("/api/transactions")
def api_create_transaction():
    data = request.get_json(silent=True) or {}
    try:
        tx_id = models.create_transaction(
            kind=data.get("kind"),
            amount=data.get("amount"),
            date=data.get("date"),
            description=data.get("description", ""),
            category_id=data.get("category_id"),
        )
    except ValueError as e:
        # Error de validación: lo causó el usuario, devolvemos 400 con el motivo.
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": tx_id}), 201


@app.delete("/api/transactions/<int:transaction_id>")
def api_delete_transaction(transaction_id):
    deleted = models.delete_transaction(transaction_id)
    if not deleted:
        return jsonify({"error": "No se encontró el movimiento."}), 404
    return jsonify({"ok": True})


@app.get("/api/categories")
def api_list_categories():
    kind = request.args.get("kind")
    return jsonify(models.list_categories(kind=kind))


@app.post("/api/categories")
def api_create_category():
    data = request.get_json(silent=True) or {}
    try:
        cat_id = models.create_category(
            name=data.get("name"), kind=data.get("kind")
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": cat_id}), 201


@app.get("/api/expenses-by-category")
def api_expenses_by_category():
    return jsonify(models.get_expense_by_category())


if __name__ == "__main__":
    # debug=True recarga al guardar cambios; solo para desarrollo local.
    app.run(host="127.0.0.1", port=5000, debug=True)
