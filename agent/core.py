"""Orquestador del Agente de Solicitudes Académicas.

Tiene dos caminos (flujo híbrido, como en la guía, Fase 7):

1. procesar_solicitud(solicitud_id): flujo FIJO y determinista.
   Llama las tools en orden, el planner decide con reglas y se ejecutan las
   acciones. No usa el LLM: es trazable y funciona aunque Gemini falle.

2. crear_agente(memoria): agente conversacional con Gemini (LangChain).
   El LLM elige qué tools usar para responder preguntas abiertas. NO tiene
   acceso directo a las tools de escritura: para resolver una solicitud debe
   llamar a procesar_solicitud_completa, que pasa siempre por el planner.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from agent.memory.short_term import crear_memoria_corto_plazo
from agent.planner import construir_estado, decidir_accion
from agent.tools.buscar_reglamento import buscar_reglamento
from agent.tools.consultar_alumno import consultar_alumno
from agent.tools.consultar_solicitud import consultar_solicitud
from agent.tools.notificar_alumno import notificar_alumno
from agent.tools.registrar_decision import registrar_decision
from agent.tools.validar_plazo import validar_plazo
from config.settings import GOOGLE_API_KEY, LLM_MODEL, NOMBRE_INSTITUCION

TIPO_LEGIBLE = {
    "justificacion_inasistencia": "justificación de inasistencia",
    "prorroga_entrega": "prórroga de entrega",
}

# Mensaje que recibe el alumno según la acción
MENSAJES = {
    "aprobar_automatico": "Tu solicitud {id} fue aprobada.",
    "solicitar_info": "Tu solicitud {id} está pendiente: adjunta el documento de respaldo.",
    "derivar_coordinacion": "Tu solicitud {id} fue derivada a coordinación académica.",
    "derivar_docente": "Tu solicitud {id} fue derivada al docente de la asignatura.",
    "derivar_revision": "Tu solicitud {id} quedó en revisión por coordinación académica.",
}


# ---------------------------------------------------------------------------
# Camino 1: flujo determinista (lo usa la pestaña "Procesar" de Streamlit)
# ---------------------------------------------------------------------------
def procesar_solicitud(solicitud_id: str) -> dict:
    """Procesa una solicitud de principio a fin y devuelve la decisión con su traza."""
    traza = []  # registro paso a paso de lo que hizo el agente

    # 1. Percibir: leer la solicitud
    solicitud = consultar_solicitud.invoke({"solicitud_id": solicitud_id})
    traza.append({"paso": 1, "tool": "consultar_solicitud",
                  "detalle": solicitud.get("error") or
                  f"{solicitud['tipo']} de {solicitud['alumno_id']} ({solicitud['asignatura']})"})
    if "error" in solicitud:
        return {"ok": False, "error": solicitud["error"], "traza": traza}

    # Evita procesar dos veces la misma solicitud (duplicaría la memoria)
    if solicitud["estado"] != "pendiente":
        return {"ok": False, "traza": traza,
                "error": f"La solicitud {solicitud_id} ya fue procesada "
                         f"(estado: {solicitud['estado']}). Reinicia los datos para repetirla."}

    # 2. Recordar: datos del alumno + historial (memoria de largo plazo)
    alumno = consultar_alumno.invoke({"alumno_id": solicitud["alumno_id"]})
    traza.append({"paso": 2, "tool": "consultar_alumno",
                  "detalle": f"{alumno.get('nombre')}: {alumno.get('justificaciones_semestre', 0)} "
                             f"justificaciones aprobadas este semestre"})

    # 3. Razonar: ¿está en plazo?
    plazo = validar_plazo.invoke({"solicitud_id": solicitud_id})
    traza.append({"paso": 3, "tool": "validar_plazo", "detalle": plazo["razon"]})

    # 4. Decidir: el planner aplica las reglas en orden
    estado = construir_estado(solicitud, alumno, plazo)
    accion = decidir_accion(estado)
    traza.append({"paso": 4, "tool": "planner",
                  "detalle": f"Regla {accion.regla} -> {accion.tipo}: {accion.razon}"})

    # 5. Justificar: buscar el artículo del reglamento que respalda la decisión (RAG)
    consulta = f"{TIPO_LEGIBLE.get(solicitud['tipo'], solicitud['tipo'])}: {accion.razon}"
    fundamento = buscar_reglamento.invoke({"consulta": consulta, "k": 2})
    traza.append({"paso": 5, "tool": "buscar_reglamento",
                  "detalle": ", ".join(f.get("articulo") or f.get("error", "")
                                       for f in fundamento)})

    # 6. Actuar: registrar la decisión (memoria) y avisar al alumno
    registro = registrar_decision.invoke({"solicitud_id": solicitud_id,
                                          "decision": accion.tipo,
                                          "razon": accion.razon})
    traza.append({"paso": 6, "tool": "registrar_decision",
                  "detalle": f"Estado: {registro.get('estado')}"})

    mensaje = MENSAJES[accion.tipo].format(id=solicitud_id) + f" Motivo: {accion.razon}."
    notificacion = notificar_alumno.invoke({"alumno_id": solicitud["alumno_id"],
                                            "mensaje": mensaje})
    traza.append({"paso": 7, "tool": "notificar_alumno",
                  "detalle": f"Enviado por {notificacion['canal']}"})

    return {
        "ok": True,
        "solicitud_id": solicitud_id,
        "accion": accion.tipo,
        "regla": accion.regla,
        "razon": accion.razon,
        "fundamento": fundamento,
        "solicitud": solicitud,
        "alumno": alumno,
        "plazo": plazo,
        "mensaje_alumno": mensaje,
        "traza": traza,
    }


@tool
def procesar_solicitud_completa(solicitud_id: str) -> dict:
    """Resuelve una solicitud pendiente (formato SOL-001) aplicando las reglas del reglamento.

    Consulta la solicitud y al alumno, valida el plazo, decide con las reglas,
    registra la decisión y notifica al alumno. Úsala cuando te pidan procesar,
    resolver o aprobar una solicitud. Devuelve la acción, la regla y la razón.
    """
    r = procesar_solicitud(solicitud_id)
    if not r["ok"]:
        return {"error": r["error"]}
    return {"accion": r["accion"], "regla": r["regla"], "razon": r["razon"],
            "articulos": [f.get("articulo") for f in r["fundamento"]]}


# ---------------------------------------------------------------------------
# Camino 2: agente conversacional con LLM (pestaña "Chat" de Streamlit)
# ---------------------------------------------------------------------------
# Solo tools de lectura + el flujo completo. Las de escritura no se exponen
# al LLM: así no puede saltarse el planner aunque se lo pidan en el chat.
TOOLS_LLM = [consultar_solicitud, consultar_alumno, validar_plazo,
             buscar_reglamento, procesar_solicitud_completa]

SYSTEM_PROMPT = f"""Eres el asistente de coordinación académica de {NOMBRE_INSTITUCION}.
Ayudas a funcionarios a revisar solicitudes de estudiantes (justificaciones de
inasistencia y prórrogas de entrega).

Cómo trabajas:
1. Si te preguntan por una solicitud o un alumno, consulta los datos con tus
   herramientas. Nunca inventes datos.
2. Si te preguntan por normas, plazos o requisitos, usa buscar_reglamento y
   cita el artículo.
3. Si te piden resolver o procesar una solicitud, usa procesar_solicitud_completa.
   Tú no decides aprobar ni rechazar: la decisión la toman las reglas.
4. Si piden algo fuera de tu alcance, dilo y sugiere derivar a coordinación.
Responde en español, breve y claro."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),  # aquí entra la memoria de corto plazo
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # aquí van las tools usadas en este turno
])


def crear_agente(memoria=None) -> AgentExecutor:
    """Crea el agente conversacional (Gemini + tools + memoria de corto plazo)."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if memoria is None:
        memoria = crear_memoria_corto_plazo()
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY,
                                 temperature=0.2)
    agente = create_tool_calling_agent(llm, TOOLS_LLM, PROMPT)
    return AgentExecutor(agent=agente, tools=TOOLS_LLM, memory=memoria,
                         verbose=True, max_iterations=6,
                         handle_parsing_errors=True)
