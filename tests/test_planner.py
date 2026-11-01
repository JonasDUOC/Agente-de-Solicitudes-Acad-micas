"""Tests del planner: una prueba por regla + pruebas de prioridad."""
from agent.planner import decidir_accion

# Estado base: un caso estándar que cumple todo. Cada test cambia solo lo necesario.
BASE = {"tipo": "justificacion_inasistencia", "en_plazo": True,
        "afecta_evaluacion": False, "dias_solicitados": 0,
        "justificaciones_previas": 0, "tiene_respaldo": True}


def estado(**cambios):
    return {**BASE, **cambios}


def test_regla0_tipo_fuera_de_alcance():
    a = decidir_accion(estado(tipo="retiro_asignatura"))
    assert (a.regla, a.tipo) == (0, "derivar_coordinacion")


def test_regla1_fuera_de_plazo():
    a = decidir_accion(estado(en_plazo=False))
    assert (a.regla, a.tipo) == (1, "derivar_coordinacion")


def test_regla2_afecta_evaluacion():
    a = decidir_accion(estado(afecta_evaluacion=True))
    assert (a.regla, a.tipo) == (2, "derivar_docente")


def test_regla2_prorroga_larga():
    a = decidir_accion(estado(tipo="prorroga_entrega", dias_solicitados=10))
    assert (a.regla, a.tipo) == (2, "derivar_docente")


def test_prorroga_de_7_dias_no_va_al_docente():
    # Límite exacto: 7 NO es "más de 7"
    a = decidir_accion(estado(tipo="prorroga_entrega", dias_solicitados=7))
    assert a.tipo == "aprobar_automatico"


def test_regla3_tercera_justificacion():
    a = decidir_accion(estado(justificaciones_previas=2))   # esta sería la 3ª
    assert (a.regla, a.tipo) == (3, "derivar_revision")


def test_segunda_justificacion_se_aprueba():
    a = decidir_accion(estado(justificaciones_previas=1))   # esta sería la 2ª
    assert a.tipo == "aprobar_automatico"


def test_regla4_sin_respaldo():
    a = decidir_accion(estado(tiene_respaldo=False))
    assert (a.regla, a.tipo) == (4, "solicitar_info")


def test_regla5_caso_estandar():
    a = decidir_accion(estado())
    assert (a.regla, a.tipo) == (5, "aprobar_automatico")


def test_prioridad_fuera_de_plazo_gana_a_todo():
    # Cumple reglas 1, 2 y 4 a la vez: gana la 1 porque se evalúa primero
    a = decidir_accion(estado(tipo="prorroga_entrega", en_plazo=False,
                              dias_solicitados=10, tiene_respaldo=False))
    assert a.regla == 1
