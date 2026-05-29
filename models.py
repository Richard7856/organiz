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
