"""Tool (escritura): registra la decisión del agente.

Hace dos cosas:
1. Cambia el estado de la solicitud (pendiente -> aprobada / derivada / ...).
2. Guarda la decisión en el historial (memoria de largo plazo).
"""
import sqlite3

from langchain_core.tools import tool

from agent.memory.long_term import guardar_decision
from config.settings import DB_PATH

# Qué estado queda en la solicitud según la acción del planner
ESTADO_POR_ACCION = {
    "aprobar_automatico": "aprobada",
    "solicitar_info": "pendiente_info",
    "derivar_coordinacion": "derivada_coordinacion",
    "derivar_docente": "derivada_docente",
    "derivar_revision": "derivada_revision",
}


@tool
def registrar_decision(solicitud_id: str, decision: str, razon: str) -> dict:
    """Registra la decisión tomada sobre una solicitud y la guarda en el historial.

    decision debe ser una de: aprobar_automatico, solicitar_info,
    derivar_coordinacion, derivar_docente, derivar_revision.
    Devuelve {'ok': bool, 'estado': str}.
    """
    if decision not in ESTADO_POR_ACCION:
        return {"ok": False, "error": f"Decisión no válida: {decision}"}

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT alumno_id, tipo FROM solicitudes WHERE solicitud_id = ?",
        (solicitud_id,),
    ).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "error": f"Solicitud {solicitud_id} no encontrada"}

    estado = ESTADO_POR_ACCION[decision]
    conn.execute("UPDATE solicitudes SET estado = ? WHERE solicitud_id = ?",
                 (estado, solicitud_id))
    conn.commit()
    conn.close()

    guardar_decision(solicitud_id, row[0], row[1], decision, razon)
    return {"ok": True, "estado": estado}
