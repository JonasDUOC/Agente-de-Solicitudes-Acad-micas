"""Carga los CSV en SQLite y crea las tablas de memoria.

Ejecutar desde la raíz:  python -m scripts.seed_data
OJO: borra y recrea todo, incluido el historial (memoria de largo plazo).
Úsalo para dejar la demo en su estado inicial.
"""
import sqlite3

import pandas as pd

from config.settings import DATA_DIR, DB_PATH

ESQUEMA = """
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS solicitudes;
DROP TABLE IF EXISTS historial;
DROP TABLE IF EXISTS notificaciones;

CREATE TABLE alumnos (
    alumno_id TEXT PRIMARY KEY,
    nombre    TEXT,
    email     TEXT,
    carrera   TEXT
);

CREATE TABLE solicitudes (
    solicitud_id      TEXT PRIMARY KEY,
    alumno_id         TEXT,
    tipo              TEXT,
    asignatura        TEXT,
    fecha_evento      TEXT,
    fecha_solicitud   TEXT,
    dias_solicitados  INTEGER,
    afecta_evaluacion INTEGER,   -- 0/1 (SQLite no tiene booleanos)
    tiene_respaldo    INTEGER,   -- 0/1
    descripcion       TEXT,
    estado            TEXT
);

-- Memoria de largo plazo: decisiones que toma el propio agente.
CREATE TABLE historial (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id TEXT,
    alumno_id    TEXT,
    tipo         TEXT,
    decision     TEXT,
    razon        TEXT,
    semestre     TEXT,
    fecha        TEXT
);

-- Registro de notificaciones simuladas (en un sistema real sería un correo).
CREATE TABLE notificaciones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id TEXT,
    mensaje   TEXT,
    canal     TEXT,
    fecha     TEXT
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(ESQUEMA)
    pd.read_csv(DATA_DIR / "alumnos.csv").to_sql(
        "alumnos", conn, if_exists="append", index=False)
    pd.read_csv(DATA_DIR / "solicitudes.csv").to_sql(
        "solicitudes", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"[OK] SQLite listo en {DB_PATH}")


if __name__ == "__main__":
    main()
