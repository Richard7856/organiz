"""Punto de entrada para Vercel (Python serverless).

Vercel busca un objeto WSGI llamado `app` en el archivo del build. Reutilizamos
la app Flask definida en app.py sin cambios. Al estar en la raíz del proyecto,
los imports y los globs de includeFiles (en vercel.json) quedan simples.
"""

from app import app  # noqa: F401  (Vercel usa este objeto WSGI)
