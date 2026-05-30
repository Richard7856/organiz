"""Lógica de acceso a datos para ingresos, gastos y categorías.

Cada función abre y cierra su propia conexión. Las rutas de Flask llaman
a estas funciones y nunca escriben SQL directamente, así la lógica de
negocio queda en un único lugar fácil de probar y de evolucionar.
"""

from database import get_db


# --------------------------------------------------------------------------- #
# Categorías
# --------------------------------------------------------------------------- #
def list_categories(kind=None):
    """Lista las categorías, opcionalmente filtradas por 'income' o 'expense'."""
    conn = get_db()
    try:
        if kind:
            rows = conn.execute(
                "SELECT * FROM categories WHERE kind = ? ORDER BY name",
                (kind,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM categories ORDER BY kind, name"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_category(name, kind):
    """Crea una categoría y devuelve su id. Lanza ValueError si los datos fallan."""
    name = (name or "").strip()
    if not name:
        raise ValueError("El nombre de la categoría no puede estar vacío.")
    if kind not in ("income", "expense"):
        raise ValueError("El tipo debe ser 'income' o 'expense'.")

    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO categories (name, kind) VALUES (?, ?)", (name, kind)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Transacciones (ingresos y gastos)
# --------------------------------------------------------------------------- #
def list_transactions(kind=None, limit=None):
    """Lista movimientos (más recientes primero) con el nombre de su categoría."""
    query = """
        SELECT t.*, c.name AS category_name
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
    """
    params = []
    if kind:
        query += " WHERE t.kind = ?"
        params.append(kind)
    query += " ORDER BY t.date DESC, t.id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    conn = get_db()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_transaction(kind, amount, date, description="", category_id=None):
    """Registra un ingreso o gasto y devuelve su id.

    Valida los datos y lanza ValueError con un mensaje claro si algo no cuadra,
    para que la ruta lo traduzca en una respuesta de error legible.
    """
    if kind not in ("income", "expense"):
        raise ValueError("El tipo debe ser 'income' (ingreso) o 'expense' (gasto).")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("El importe debe ser un número.")
    if amount <= 0:
        raise ValueError("El importe debe ser mayor que cero.")

    date = (date or "").strip()
    if not date:
        raise ValueError("La fecha es obligatoria.")

    description = (description or "").strip()
    category_id = int(category_id) if category_id else None

    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO transactions (kind, amount, description, date, category_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (kind, amount, description, date, category_id),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_transaction(transaction_id):
    """Borra un movimiento. Devuelve True si existía y se eliminó."""
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM transactions WHERE id = ?", (transaction_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Resumen / panel
# --------------------------------------------------------------------------- #
def get_summary():
    """Devuelve totales de ingresos, gastos y balance.

    El balance se calcula en SQL para que sea coherente aunque haya muchos
    movimientos.
    """
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN kind = 'income'  THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount END), 0) AS total_expense
            FROM transactions
            """
        ).fetchone()
        total_income = row["total_income"]
        total_expense = row["total_expense"]
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }
    finally:
        conn.close()


def get_expense_by_category():
    """Suma de gastos agrupada por categoría (para gráficos del panel)."""
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT COALESCE(c.name, 'Sin categoría') AS category_name,
                   SUM(t.amount) AS total
            FROM transactions t
            LEFT JOIN categories c ON c.id = t.category_id
            WHERE t.kind = 'expense'
            GROUP BY t.category_id
            ORDER BY total DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Fase 2: proyectos
# --------------------------------------------------------------------------- #
PROJECT_STATUSES = ("active", "paused", "completed")


def list_projects():
    """Lista los proyectos con su número de avances y su progreso más reciente.

    El progreso de un proyecto es el porcentaje del avance más reciente que
    tenga un valor; así la lista refleja "cómo va" sin cálculos en el frontend.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT
                p.*,
                (SELECT COUNT(*) FROM progress_updates u
                     WHERE u.project_id = p.id) AS updates_count,
                (SELECT u.progress FROM progress_updates u
                     WHERE u.project_id = p.id AND u.progress IS NOT NULL
                     ORDER BY u.date DESC, u.id DESC LIMIT 1) AS latest_progress
            FROM projects p
            ORDER BY p.created_at DESC, p.id DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_project(project_id):
    """Devuelve un proyecto por su id, o None si no existe."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_project(name, description="", status="active"):
    """Crea un proyecto y devuelve su id. Lanza ValueError si los datos fallan."""
    name = (name or "").strip()
    if not name:
        raise ValueError("El nombre del proyecto no puede estar vacío.")
    if status not in PROJECT_STATUSES:
        raise ValueError("Estado de proyecto no válido.")

    description = (description or "").strip()

    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO projects (name, description, status) VALUES (?, ?, ?)",
            (name, description, status),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_project(project_id, name=None, description=None, status=None):
    """Actualiza los campos indicados de un proyecto. Devuelve True si existía."""
    fields = []
    params = []
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("El nombre del proyecto no puede estar vacío.")
        fields.append("name = ?")
        params.append(name)
    if description is not None:
        fields.append("description = ?")
        params.append(description.strip())
    if status is not None:
        if status not in PROJECT_STATUSES:
            raise ValueError("Estado de proyecto no válido.")
        fields.append("status = ?")
        params.append(status)

    if not fields:
        return True  # Nada que actualizar.

    params.append(project_id)
    conn = get_db()
    try:
        cur = conn.execute(
            f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", params
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_project(project_id):
    """Borra un proyecto y, en cascada, todos sus avances."""
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Fase 2: avances de un proyecto
# --------------------------------------------------------------------------- #
def list_progress(project_id):
    """Lista los avances de un proyecto, del más reciente al más antiguo."""
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT * FROM progress_updates
            WHERE project_id = ?
            ORDER BY date DESC, id DESC
            """,
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_progress(project_id, note, date, progress=None):
    """Registra un avance en un proyecto y devuelve su id.

    Valida que el proyecto exista y que el porcentaje (si se da) esté entre
    0 y 100.
    """
    if get_project(project_id) is None:
        raise ValueError("El proyecto no existe.")

    note = (note or "").strip()
    date = (date or "").strip()
    if not date:
        raise ValueError("La fecha es obligatoria.")
    if not note and progress is None:
        raise ValueError("Escribe una nota o indica un porcentaje de avance.")

    if progress is not None and progress != "":
        try:
            progress = int(progress)
        except (TypeError, ValueError):
            raise ValueError("El porcentaje debe ser un número entero.")
        if not 0 <= progress <= 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100.")
    else:
        progress = None

    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO progress_updates (project_id, note, progress, date)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, note, progress, date),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_progress(progress_id):
    """Borra un avance concreto. Devuelve True si existía."""
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM progress_updates WHERE id = ?", (progress_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
