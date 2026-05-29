# 💰 Organiz

Organizador personal de **ingresos y gastos**. Registras lo que entra y lo que
sale, y la app te muestra el balance al instante.

> **Fase 1 (actual):** ingresos y gastos.
> **Fase 2 (planeada):** subir proyectos y registrar avances.

## Tecnología

- **Backend:** Python + [Flask](https://flask.palletsprojects.com/)
- **Base de datos:** SQLite (archivo local `organiz.db`)
- **Frontend:** HTML + CSS + JavaScript (sin frameworks, sin dependencias extra)

## Requisitos

- Python 3.9 o superior

## Instalación y uso

```bash
# 1. (Recomendado) crear un entorno virtual
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar la app
python app.py
```

Luego abre tu navegador en **http://127.0.0.1:5000**.

La primera vez se crea automáticamente la base de datos `organiz.db` con un
conjunto de categorías por defecto (Sueldo, Comida, Transporte…).

## Estructura del proyecto

```
organiz/
├── app.py            # App Flask: páginas y API JSON
├── database.py       # Conexión a SQLite e inicialización
├── models.py         # Acceso a datos (ingresos, gastos, categorías)
├── schema.sql        # Definición de las tablas
├── requirements.txt  # Dependencias de Python
├── templates/        # Plantillas HTML
│   ├── base.html
│   └── index.html
└── static/           # Recursos del frontend
    ├── css/style.css
    └── js/app.js
```

## API

| Método | Ruta                          | Descripción                          |
|--------|-------------------------------|--------------------------------------|
| GET    | `/api/summary`                | Totales de ingresos, gastos y balance|
| GET    | `/api/transactions`           | Lista de movimientos                 |
| POST   | `/api/transactions`           | Crea un ingreso o gasto              |
| DELETE | `/api/transactions/<id>`      | Elimina un movimiento                |
| GET    | `/api/categories`             | Lista de categorías                  |
| POST   | `/api/categories`             | Crea una categoría                   |
| GET    | `/api/expenses-by-category`   | Gastos agrupados por categoría       |

## Hoja de ruta

- [x] **Fase 1** — Registro de ingresos y gastos, balance y categorías.
- [ ] **Fase 2** — Proyectos y avances: subir proyectos y registrar progreso.

---

Hecho con cariño para llevar mis finanzas en orden. 🙂
