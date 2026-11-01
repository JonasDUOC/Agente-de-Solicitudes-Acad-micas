"""Tool (consulta): datos del alumno + su historial (memoria de largo plazo)."""
import sqlite3

from langchain_core.tools import tool

from agent.memory.long_term import contar_justificaciones_aprobadas, obtener_historial
from config.settings import DB_PATH


@tool
def consultar_alumno(alumno_id: str) -> dict:
    """Consulta los datos de un alumno por su ID (formato ALU-001) y su historial.

    Devuelve nombre, email, carrera, las últimas decisiones que el agente tomó
    sobre sus solicitudes (historial) y cuántas justificaciones de inasistencia
    se le aprobaron este semestre. Si no existe, devuelve {'error': '...'}.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM alumnos WHERE alumno_id = ?", (alumno_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"error": f"Alumno {alumno_id} no encontrado"}
    alumno = dict(row)
    # Aquí entra la memoria: cada vez que se mira al alumno, se ve su pasado
    alumno["historial"] = obtener_historial(alumno_id, limite=5)
    alumno["justificaciones_semestre"] = contar_justificaciones_aprobadas(alumno_id)
    return alumno


if __name__ == "__main__":
    print(consultar_alumno.invoke({"alumno_id": "ALU-001"}))
