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

-- --------------------------------------------------------------------------- --
-- Fase 2: proyectos y avances
-- --------------------------------------------------------------------------- --

-- Un proyecto que el usuario quiere seguir (su descripción y estado).
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    -- 'active' (en curso), 'paused' (en pausa) o 'completed' (terminado).
    status      TEXT    NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'paused', 'completed')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Cada avance/nota de progreso registrado en un proyecto.
CREATE TABLE IF NOT EXISTS progress_updates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Si se borra el proyecto, sus avances se borran con él (CASCADE).
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    note        TEXT    NOT NULL DEFAULT '',
    -- Porcentaje de avance acumulado (0-100). Opcional.
    progress    INTEGER CHECK (progress IS NULL OR (progress >= 0 AND progress <= 100)),
    date        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_progress_project ON progress_updates(project_id);
