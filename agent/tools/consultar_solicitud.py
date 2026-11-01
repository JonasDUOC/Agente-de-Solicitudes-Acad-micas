"""Tool (consulta): obtiene una solicitud por su ID."""
import sqlite3

from langchain_core.tools import tool

from config.settings import DB_PATH


@tool
def consultar_solicitud(solicitud_id: str) -> dict:
    """Consulta una solicitud académica por su ID (formato SOL-001).

    Devuelve un dict con alumno_id, tipo, asignatura, fecha_evento,
    fecha_solicitud, dias_solicitados, afecta_evaluacion, tiene_respaldo,
    descripcion y estado. Si no existe, devuelve {'error': '...'}.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM solicitudes WHERE solicitud_id = ?", (solicitud_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"error": f"Solicitud {solicitud_id} no encontrada"}
    solicitud = dict(row)
    # SQLite guarda 0/1: los pasamos a True/False para que se lean mejor
    solicitud["afecta_evaluacion"] = bool(solicitud["afecta_evaluacion"])
    solicitud["tiene_respaldo"] = bool(solicitud["tiene_respaldo"])
    return solicitud


if __name__ == "__main__":
    print(consultar_solicitud.invoke({"solicitud_id": "SOL-001"}))
