# 💰 Organiz

Organizador personal de **finanzas y proyectos**. Registras tus ingresos y
gastos (y ves el balance al instante), y además llevas tus proyectos con sus
avances.

> **Fase 1:** ingresos y gastos. ✅
> **Fase 2:** proyectos y avances (con % de progreso y línea de tiempo). ✅

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
├── app.py                 # App Flask: páginas y API JSON
├── index.py               # Punto de entrada para Vercel
├── vercel.json            # Configuración de despliegue en Vercel
├── database.py            # Conexión a SQLite e inicialización
├── models.py              # Acceso a datos (finanzas y proyectos)
├── schema.sql             # Definición de las tablas
├── requirements.txt       # Dependencias de Python
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── index.html              # Panel de finanzas (Fase 1)
│   ├── projects.html           # Listado de proyectos (Fase 2)
│   ├── project_detail.html     # Detalle y avances (Fase 2)
│   └── not_found.html
└── static/
    ├── css/style.css
    └── js/
        ├── app.js              # Lógica del panel de finanzas
        ├── projects.js         # Lógica del listado de proyectos
        └── project_detail.js   # Lógica del detalle de proyecto
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
| GET    | `/api/projects`               | Lista de proyectos (con su progreso) |
| POST   | `/api/projects`               | Crea un proyecto                     |
| PATCH  | `/api/projects/<id>`          | Actualiza un proyecto (p.ej. estado) |
| DELETE | `/api/projects/<id>`          | Elimina un proyecto y sus avances    |
| GET    | `/api/projects/<id>/progress` | Lista los avances de un proyecto     |
| POST   | `/api/projects/<id>/progress` | Registra un avance                   |
| DELETE | `/api/progress/<id>`          | Elimina un avance                    |

## Desplegar en Vercel

El proyecto incluye `vercel.json` e `index.py` listos para desplegar:

```bash
npm i -g vercel   # si no lo tienes
vercel            # primer despliegue (sigue las preguntas)
vercel --prod     # despliegue a producción
```

> ⚠️ **Importante sobre los datos en Vercel.** Vercel es *serverless*: el disco
> es de solo lectura salvo `/tmp`, que es **efímero**. La app arranca y funciona,
> pero **los datos se borran** entre despliegues o cuando la función "duerme".
>
> - Para **probar y usar de verdad con tus datos**, ejecútala **en local** (la
>   base de datos `organiz.db` persiste en tu disco).
> - Para una versión en la nube con datos persistentes, hay que conectar una
>   **base de datos gestionada** (por ejemplo Vercel Postgres o Supabase). Es un
>   paso natural para más adelante.

## Hoja de ruta

- [x] **Fase 1** — Registro de ingresos y gastos, balance y categorías.
- [x] **Fase 2** — Proyectos y avances: crear proyectos, registrar progreso (%)
      y ver la línea de tiempo de avances.
- [ ] **Próximo** — Persistencia en la nube (base de datos gestionada) y, quizá,
      cuentas de usuario y gráficos.

---

Hecho con cariño para llevar mis finanzas y proyectos en orden. 🙂
