"""Tool (escritura): notificación simulada al alumno.

En un sistema real aquí se enviaría un correo. Lo simulamos guardando el
mensaje en la tabla notificaciones (así queda evidencia) e imprimiéndolo.
"""
import sqlite3
from datetime import datetime

from langchain_core.tools import tool

from config.settings import DB_PATH


@tool
def notificar_alumno(alumno_id: str, mensaje: str) -> dict:
    """Envía (simulado) un mensaje al alumno sobre el estado de su solicitud.

    Devuelve {'ok': bool, 'canal': str}.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO notificaciones (alumno_id, mensaje, canal, fecha) VALUES (?, ?, ?, ?)",
        (alumno_id, mensaje, "email_simulado",
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    print(f"[NOTIF] -> {alumno_id}: {mensaje}")
    return {"ok": True, "canal": "email_simulado"}
