"""Tool (razonamiento): verifica si la solicitud se presentó dentro de plazo.

Solo INFORMA (en plazo o no). No decide qué hacer: eso es trabajo del planner.
"""
import sqlite3
from datetime import datetime

from langchain_core.tools import tool

from config.settings import DB_PATH, PLAZO_PRESENTACION_DIAS


@tool
def validar_plazo(solicitud_id: str) -> dict:
    """Verifica si una solicitud se presentó dentro del plazo del reglamento.

    Compara la fecha del evento (inasistencia o entrega original) con la fecha
    en que se presentó la solicitud. Devuelve {'en_plazo': bool,
    'dias_desde_evento': int, 'plazo_maximo': int, 'razon': str}.
    """
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT fecha_evento, fecha_solicitud FROM solicitudes WHERE solicitud_id = ?",
        (solicitud_id,),
    ).fetchone()
    conn.close()
    if not row:
        return {"en_plazo": False, "dias_desde_evento": -1,
                "plazo_maximo": PLAZO_PRESENTACION_DIAS,
                "razon": "Solicitud no encontrada"}

    evento = datetime.strptime(row[0], "%Y-%m-%d")
    presentada = datetime.strptime(row[1], "%Y-%m-%d")
    dias = (presentada - evento).days   # negativo = se pidió antes del evento

    if dias > PLAZO_PRESENTACION_DIAS:
        return {"en_plazo": False, "dias_desde_evento": dias,
                "plazo_maximo": PLAZO_PRESENTACION_DIAS,
                "razon": f"Presentada {dias} días después del evento "
                         f"(máximo {PLAZO_PRESENTACION_DIAS})"}
    return {"en_plazo": True, "dias_desde_evento": dias,
            "plazo_maximo": PLAZO_PRESENTACION_DIAS,
            "razon": "Presentada dentro de plazo"}


if __name__ == "__main__":
    print(validar_plazo.invoke({"solicitud_id": "SOL-002"}))
