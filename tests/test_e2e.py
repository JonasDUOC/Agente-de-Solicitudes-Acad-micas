"""Tests end-to-end: recorren todo el flujo de procesar_solicitud."""
from agent.core import procesar_solicitud
from agent.memory.long_term import obtener_historial


def test_caso_estandar_se_aprueba():
    r = procesar_solicitud("SOL-001")
    assert r["ok"] is True
    assert r["accion"] == "aprobar_automatico"
    assert len(r["traza"]) == 7          # los 7 pasos del flujo


def test_fuera_de_plazo_se_deriva_a_coordinacion():
    r = procesar_solicitud("SOL-002")
    assert r["accion"] == "derivar_coordinacion"
    assert r["regla"] == 1


def test_evaluacion_se_deriva_al_docente():
    assert procesar_solicitud("SOL-003")["accion"] == "derivar_docente"


def test_sin_respaldo_pide_informacion():
    assert procesar_solicitud("SOL-005")["accion"] == "solicitar_info"


def test_tramite_fuera_de_alcance():
    r = procesar_solicitud("SOL-007")
    assert (r["regla"], r["accion"]) == (0, "derivar_coordinacion")


def test_memoria_cambia_la_decision():
    # Mismo alumno (ALU-004), tres justificaciones iguales en orden.
    # La memoria de largo plazo hace que la tercera ya no se apruebe sola.
    assert procesar_solicitud("SOL-008")["accion"] == "aprobar_automatico"
    assert procesar_solicitud("SOL-009")["accion"] == "aprobar_automatico"
    r = procesar_solicitud("SOL-010")
    assert r["accion"] == "derivar_revision"
    assert len(obtener_historial("ALU-004")) == 3


def test_no_procesa_dos_veces():
    procesar_solicitud("SOL-001")
    r = procesar_solicitud("SOL-001")
    assert r["ok"] is False


def test_solicitud_inexistente():
    assert procesar_solicitud("SOL-999")["ok"] is False
