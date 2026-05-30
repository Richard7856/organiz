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


@app.route("/projects")
def projects_page():
    """Listado de proyectos y formulario para crear uno (Fase 2)."""
    return render_template("projects.html")


@app.route("/projects/<int:project_id>")
def project_detail_page(project_id):
    """Detalle de un proyecto con sus avances (Fase 2)."""
    project = models.get_project(project_id)
    if project is None:
        return render_template("not_found.html"), 404
    return render_template("project_detail.html", project=project)


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


# --------------------------------------------------------------------------- #
# API JSON — Fase 2: proyectos y avances
# --------------------------------------------------------------------------- #
@app.get("/api/projects")
def api_list_projects():
    return jsonify(models.list_projects())


@app.post("/api/projects")
def api_create_project():
    data = request.get_json(silent=True) or {}
    try:
        project_id = models.create_project(
            name=data.get("name"),
            description=data.get("description", ""),
            status=data.get("status", "active"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": project_id}), 201


@app.patch("/api/projects/<int:project_id>")
def api_update_project(project_id):
    data = request.get_json(silent=True) or {}
    try:
        updated = models.update_project(
            project_id,
            name=data.get("name"),
            description=data.get("description"),
            status=data.get("status"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not updated:
        return jsonify({"error": "No se encontró el proyecto."}), 404
    return jsonify({"ok": True})


@app.delete("/api/projects/<int:project_id>")
def api_delete_project(project_id):
    if not models.delete_project(project_id):
        return jsonify({"error": "No se encontró el proyecto."}), 404
    return jsonify({"ok": True})


@app.get("/api/projects/<int:project_id>/progress")
def api_list_progress(project_id):
    if models.get_project(project_id) is None:
        return jsonify({"error": "No se encontró el proyecto."}), 404
    return jsonify(models.list_progress(project_id))


@app.post("/api/projects/<int:project_id>/progress")
def api_create_progress(project_id):
    data = request.get_json(silent=True) or {}
    try:
        update_id = models.create_progress(
            project_id,
            note=data.get("note", ""),
            date=data.get("date"),
            progress=data.get("progress"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": update_id}), 201


@app.delete("/api/progress/<int:progress_id>")
def api_delete_progress(progress_id):
    if not models.delete_progress(progress_id):
        return jsonify({"error": "No se encontró el avance."}), 404
    return jsonify({"ok": True})


if __name__ == "__main__":
    # debug=True recarga al guardar cambios; solo para desarrollo local.
    app.run(host="127.0.0.1", port=5000, debug=True)
