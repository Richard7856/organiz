"""Acceso a la base de datos SQLite.

Centraliza la conexión y la inicialización del esquema. El resto de la
aplicación pide conexiones a través de get_db() y nunca abre SQLite por
su cuenta, de modo que cambiar de motor en el futuro afecta solo a este
archivo.
"""

import os
import sqlite3

# La base de datos vive junto al código, en organiz.db. Se puede sobrescribir
# con la variable de entorno ORGANIZ_DB (útil para pruebas).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("ORGANIZ_DB", os.path.join(BASE_DIR, "organiz.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# Categorías que se crean la primera vez para que la app no arranque vacía.
DEFAULT_CATEGORIES = [
    ("Sueldo", "income"),
    ("Ventas", "income"),
    ("Otros ingresos", "income"),
    ("Comida", "expense"),
    ("Transporte", "expense"),
    ("Vivienda", "expense"),
    ("Servicios", "expense"),
    ("Ocio", "expense"),
    ("Otros gastos", "expense"),
]


def get_db():
    """Devuelve una conexión SQLite con filas accesibles por nombre de columna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Hace cumplir las claves foráneas (SQLite las ignora si no se activan).
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas (si faltan) y siembra las categorías por defecto."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    conn = get_db()
    try:
        conn.executescript(schema)

        # Solo sembramos categorías si la tabla está vacía, para no duplicar
        # ni reponer las que el usuario haya borrado a propósito.
        count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO categories (name, kind) VALUES (?, ?)",
                DEFAULT_CATEGORIES,
            )
        conn.commit()
    finally:
        conn.close()
