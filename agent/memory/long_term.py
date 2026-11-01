"""Memoria de largo plazo: historial de decisiones en SQLite.

Persiste entre sesiones: si cierras la app y la vuelves a abrir,
el agente sigue "recordando" lo que decidió antes para cada alumno.
No usa el LLM: es guardar + recuperar bien. La "inteligencia" está en
que el planner usa este historial al decidir (regla 3).
"""
import sqlite3
from datetime import datetime

from config.settings import DB_PATH, SEMESTRE_ACTUAL


def guardar_decision(solicitud_id: str, alumno_id: str, tipo: str,
                     decision: str, razon: str) -> dict:
    """Guarda una decisión del agente en el historial del alumno."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO historial (solicitud_id, alumno_id, tipo, decision, razon, semestre, fecha) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (solicitud_id, alumno_id, tipo, decision, razon, SEMESTRE_ACTUAL,
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


def obtener_historial(alumno_id: str, limite: int = 5) -> list[dict]:
    """Devuelve las últimas N decisiones registradas para el alumno."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT solicitud_id, tipo, decision, razon, fecha FROM historial "
        "WHERE alumno_id = ? ORDER BY id DESC LIMIT ?",
        (alumno_id, limite),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def contar_justificaciones_aprobadas(alumno_id: str,
                                     semestre: str = SEMESTRE_ACTUAL) -> int:
    """Cuenta las justificaciones que el agente ya aprobó este semestre."""
    conn = sqlite3.connect(DB_PATH)
    (total,) = conn.execute(
        "SELECT COUNT(*) FROM historial WHERE alumno_id = ? AND semestre = ? "
        "AND tipo = 'justificacion_inasistencia' AND decision = 'aprobar_automatico'",
        (alumno_id, semestre),
    ).fetchone()
    conn.close()
    return total
