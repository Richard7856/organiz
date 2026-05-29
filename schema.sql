-- Esquema de la base de datos de Organiz (Fase 1: ingresos y gastos)
--
-- Se mantiene simple y normalizado para que en la Fase 2 sea fácil
-- añadir nuevas tablas (por ejemplo: projects, milestones) sin tocar
-- lo ya existente.

-- Categorías para clasificar los movimientos (Comida, Sueldo, Transporte...).
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    -- 'income' (ingreso) o 'expense' (gasto): una categoría sirve para uno u otro.
    kind        TEXT    NOT NULL CHECK (kind IN ('income', 'expense')),
    UNIQUE (name, kind)
);

-- Cada ingreso o gasto registrado.
CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 'income' (ingreso) o 'expense' (gasto).
    kind        TEXT    NOT NULL CHECK (kind IN ('income', 'expense')),
    -- Importe siempre positivo; el signo lo determina 'kind'.
    amount      REAL    NOT NULL CHECK (amount > 0),
    description TEXT    NOT NULL DEFAULT '',
    -- Fecha del movimiento en formato ISO (YYYY-MM-DD).
    date        TEXT    NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_kind ON transactions(kind);
