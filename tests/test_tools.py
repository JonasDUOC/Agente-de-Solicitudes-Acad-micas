"""Tests de las tools: caso feliz y caso de error de cada una."""
from agent.tools.buscar_reglamento import buscar_reglamento
from agent.tools.consultar_alumno import consultar_alumno
from agent.tools.consultar_solicitud import consultar_solicitud
from agent.tools.notificar_alumno import notificar_alumno
from agent.tools.registrar_decision import registrar_decision
from agent.tools.validar_plazo import validar_plazo
from tests.conftest import requiere_chroma


def test_consultar_solicitud_existente():
    r = consultar_solicitud.invoke({"solicitud_id": "SOL-001"})
    assert "error" not in r
    assert r["alumno_id"] == "ALU-001"
    assert r["tiene_respaldo"] is True


def test_consultar_solicitud_inexistente():
    r = consultar_solicitud.invoke({"solicitud_id": "SOL-999"})
    assert "error" in r


def test_consultar_alumno_trae_historial():
    r = consultar_alumno.invoke({"alumno_id": "ALU-001"})
    assert r["nombre"] == "Ana Rojas"
    assert r["historial"] == []            # base recién creada: sin memoria
    assert r["justificaciones_semestre"] == 0


def test_validar_plazo_dentro():
    r = validar_plazo.invoke({"solicitud_id": "SOL-001"})   # 2 días después
    assert r["en_plazo"] is True


def test_validar_plazo_fuera():
    r = validar_plazo.invoke({"solicitud_id": "SOL-002"})   # 9 días después
    assert r["en_plazo"] is False
    assert r["dias_desde_evento"] == 9


def test_validar_plazo_pedida_antes_del_evento():
    r = validar_plazo.invoke({"solicitud_id": "SOL-004"})   # pedida 2 días antes
    assert r["en_plazo"] is True
    assert r["dias_desde_evento"] < 0


def test_registrar_decision_cambia_estado_y_guarda_memoria():
    r = registrar_decision.invoke({"solicitud_id": "SOL-001",
                                   "decision": "aprobar_automatico", "razon": "test"})
    assert r == {"ok": True, "estado": "aprobada"}
    assert consultar_solicitud.invoke({"solicitud_id": "SOL-001"})["estado"] == "aprobada"
    alumno = consultar_alumno.invoke({"alumno_id": "ALU-001"})
    assert alumno["justificaciones_semestre"] == 1


def test_registrar_decision_invalida():
    r = registrar_decision.invoke({"solicitud_id": "SOL-001",
                                   "decision": "rechazar", "razon": "test"})
    assert r["ok"] is False


def test_notificar_alumno():
    r = notificar_alumno.invoke({"alumno_id": "ALU-001", "mensaje": "Hola"})
    assert r["ok"] is True


@requiere_chroma
def test_buscar_reglamento_por_significado():
    # No dice "prórroga" ni "Artículo 3", pero significa lo mismo
    r = buscar_reglamento.invoke({"consulta": "quiero más tiempo para entregar el trabajo"})
    assert len(r) == 2
    assert any("Artículo 3" in f["articulo"] for f in r)
