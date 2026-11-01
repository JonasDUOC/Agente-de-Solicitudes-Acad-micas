"""Planner: decide la acción del agente aplicando reglas en orden de prioridad.

Es determinista (no usa el LLM): con los mismos datos, siempre la misma
decisión. Eso lo hace trazable, fácil de probar y difícil de manipular con
un texto malicioso escrito por un usuario (prompt injection).

Traduce a código la tabla de docs/reglas.md.
"""
from dataclasses import dataclass

from config.settings import (
    MAX_DIAS_PRORROGA_AUTO,
    TIPOS_SOPORTADOS,
    UMBRAL_JUSTIFICACIONES_SEMESTRE,
)


@dataclass
class Accion:
    tipo: str    # qué hace el agente (ej. "derivar_docente")
    razon: str   # por qué, en palabras simples
    regla: int   # qué regla de docs/reglas.md se activó


def construir_estado(solicitud: dict, alumno: dict, plazo: dict) -> dict:
    """Traductor: junta lo que devolvieron las tools en el formato del planner."""
    return {
        "tipo": solicitud.get("tipo", ""),
        "en_plazo": plazo.get("en_plazo", False),
        "razon_plazo": plazo.get("razon", ""),
        "afecta_evaluacion": solicitud.get("afecta_evaluacion", False),
        "dias_solicitados": solicitud.get("dias_solicitados", 0),
        "justificaciones_previas": alumno.get("justificaciones_semestre", 0),
        "tiene_respaldo": solicitud.get("tiene_respaldo", False),
    }


def decidir_accion(estado: dict) -> Accion:
    """Evalúa las reglas de arriba hacia abajo y se detiene en la primera que se cumple."""
    tipo = estado.get("tipo", "")

    # Regla 0: fuera del alcance del agente (Art. 7)
    if tipo not in TIPOS_SOPORTADOS:
        return Accion("derivar_coordinacion",
                      f"Tipo de trámite '{tipo}' fuera del alcance del agente", 0)

    # Regla 1: fuera de plazo (Art. 1 y 6). El agente no rechaza solo.
    if not estado.get("en_plazo", False):
        return Accion("derivar_coordinacion",
                      f"{estado.get('razon_plazo', 'Fuera de plazo')}. "
                      "Se recomienda rechazar; decide coordinación", 1)

    # Regla 2: afecta una evaluación o prórroga larga (Art. 2 y 3)
    if estado.get("afecta_evaluacion", False):
        return Accion("derivar_docente",
                      "Afecta una evaluación: solo el docente puede reprogramarla", 2)
    if (tipo == "prorroga_entrega"
            and estado.get("dias_solicitados", 0) > MAX_DIAS_PRORROGA_AUTO):
        return Accion("derivar_docente",
                      f"Pide {estado['dias_solicitados']} días de prórroga "
                      f"(máximo sin docente: {MAX_DIAS_PRORROGA_AUTO})", 2)

    # Regla 3: muchas justificaciones en el semestre (Art. 4). Usa la MEMORIA.
    if tipo == "justificacion_inasistencia":
        total = estado.get("justificaciones_previas", 0) + 1   # +1 = esta solicitud
        if total >= UMBRAL_JUSTIFICACIONES_SEMESTRE:
            return Accion("derivar_revision",
                          f"Sería su justificación n.° {total} del semestre "
                          f"(desde la {UMBRAL_JUSTIFICACIONES_SEMESTRE}ª pasa a revisión)", 3)

    # Regla 4: falta documento de respaldo (Art. 5)
    if not estado.get("tiene_respaldo", False):
        return Accion("solicitar_info",
                      "Falta el documento de respaldo", 4)

    # Regla 5: caso estándar
    return Accion("aprobar_automatico",
                  "Cumple todos los requisitos del reglamento", 5)
