"""Interfaz Streamlit del Agente de Solicitudes Académicas.

Ejecutar desde la raíz:  streamlit run app.py

Recordatorio: Streamlit vuelve a ejecutar este archivo completo en cada clic.
Lo que debe sobrevivir entre clics se guarda en st.session_state.
"""
import sqlite3

import pandas as pd
import streamlit as st

from agent.core import crear_agente, procesar_solicitud
import agent.gemini_patch  # noqa: F401  (compatibilidad Gemini 3 + LangChain 0.3)
from agent.memory.short_term import crear_memoria_corto_plazo
from config.settings import DB_PATH, NOMBRE_INSTITUCION
from scripts import seed_data

st.set_page_config(page_title="Agente de Solicitudes Académicas", page_icon="🎓",
                   layout="wide")

COLORES = {
    "aprobar_automatico": "green",
    "solicitar_info": "blue",
    "derivar_docente": "orange",
    "derivar_revision": "orange",
    "derivar_coordinacion": "red",
}


def leer_tabla(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def texto_de(salida) -> str:
    """Gemini a veces devuelve la respuesta como lista de partes: la unimos."""
    if isinstance(salida, list):
        return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in salida)
    return str(salida)


def reiniciar_chat():
    st.session_state.memoria = crear_memoria_corto_plazo()
    st.session_state.agente = None   # se crea al primer mensaje
    st.session_state.mensajes = []


# --- Estado de la sesión (memoria de corto plazo) ---------------------------
if "memoria" not in st.session_state:
    reiniciar_chat()
if "resultados" not in st.session_state:
    st.session_state.resultados = []

# --- Barra lateral -----------------------------------------------------------
with st.sidebar:
    st.title("🎓 Solicitudes Académicas")
    st.caption(f"{NOMBRE_INSTITUCION} · Demo EP2 ISY0101")
    st.markdown("### Escenarios de la demo")
    st.markdown(
        "- **SOL-001** caso estándar\n"
        "- **SOL-002** fuera de plazo\n"
        "- **SOL-003** día de prueba\n"
        "- **SOL-004** prórroga de 10 días\n"
        "- **SOL-005** sin respaldo\n"
        "- **SOL-007** trámite fuera de alcance\n"
        "- **SOL-008 → 009 → 010** mismo alumno (memoria)"
    )
    if st.button("🔄 Reiniciar datos de demo"):
        seed_data.main()               # borra historial y deja todo pendiente
        st.session_state.resultados = []
        reiniciar_chat()
        st.rerun()

st.title("Agente de Solicitudes Académicas")
tab_procesar, tab_chat, tab_datos = st.tabs(
    ["▶️ Procesar solicitud", "💬 Chat con el agente", "🗂️ Datos y memoria"])

# --- Pestaña 1: flujo determinista ------------------------------------------
with tab_procesar:
    pendientes = leer_tabla(
        "SELECT solicitud_id, tipo, alumno_id FROM solicitudes "
        "WHERE estado = 'pendiente' ORDER BY solicitud_id")
    if pendientes.empty:
        st.info("No quedan solicitudes pendientes. Usa 'Reiniciar datos de demo'.")
    else:
        opciones = {f"{r.solicitud_id} · {r.tipo} · {r.alumno_id}": r.solicitud_id
                    for r in pendientes.itertuples()}
        elegida = st.selectbox("Solicitud pendiente", list(opciones))
        if st.button("Procesar", type="primary"):
            with st.spinner("El agente está revisando la solicitud..."):
                st.session_state.resultados.append(procesar_solicitud(opciones[elegida]))
            st.rerun()

    if st.session_state.resultados:
        r = st.session_state.resultados[-1]
        if not r["ok"]:
            st.error(r["error"])
        else:
            st.subheader(f"Resultado de {r['solicitud_id']}")
            color = COLORES.get(r["accion"], "gray")
            st.markdown(f"### :{color}[{r['accion']}]  (regla {r['regla']})")
            st.write(f"**Razón:** {r['razon']}")
            st.write(f"**Mensaje al alumno:** {r['mensaje_alumno']}")

            with st.expander("📖 Fundamento en el reglamento (RAG)", expanded=True):
                for f in r["fundamento"]:
                    if "error" in f:
                        st.warning(f["error"])
                    else:
                        st.markdown(f"**{f['articulo']}** ({f['fuente']})")
                        st.caption(f["texto"])

            with st.expander("🔍 Traza del agente paso a paso", expanded=True):
                st.dataframe(pd.DataFrame(r["traza"]), width="stretch", hide_index=True)

            with st.expander("🧠 Memoria: historial del alumno"):
                st.write(f"Justificaciones aprobadas antes de esta solicitud: "
                         f"{r['alumno']['justificaciones_semestre']}")
                st.dataframe(pd.DataFrame(r["alumno"]["historial"]), width="stretch")

        st.divider()
        st.subheader("Procesadas en esta sesión")
        st.dataframe(pd.DataFrame(
            [{"solicitud": x["solicitud_id"], "acción": x["accion"],
              "regla": x["regla"], "razón": x["razon"]}
             for x in st.session_state.resultados if x["ok"]]),
            width="stretch", hide_index=True)

# --- Pestaña 2: agente conversacional con Gemini -----------------------------
with tab_chat:
    st.caption("Ejemplos: «¿Cuántos días tengo para justificar?», "
               "«Revisa la SOL-006», «Procésala», «¿Y por qué?»")
    if st.button("🧹 Nueva conversación"):
        reiniciar_chat()
        st.rerun()

    for m in st.session_state.mensajes:
        st.chat_message(m["rol"]).write(m["texto"])

    pregunta = st.chat_input("Escribe tu consulta")
    if pregunta:
        st.chat_message("user").write(pregunta)
        st.session_state.mensajes.append({"rol": "user", "texto": pregunta})
        try:
            if st.session_state.agente is None:
                st.session_state.agente = crear_agente(st.session_state.memoria)
            with st.spinner("Pensando..."):
                salida = st.session_state.agente.invoke({"input": pregunta})["output"]
            respuesta = texto_de(salida)
        except Exception as e:   # sin API key, sin internet, cuota agotada (429)...
            import traceback; traceback.print_exc()   # TEMPORAL
            respuesta = (f"⚠️ No pude contactar al modelo ({type(e).__name__}). "
                         "La pestaña 'Procesar solicitud' funciona sin el LLM.")
        st.chat_message("assistant").write(respuesta)
        st.session_state.mensajes.append({"rol": "assistant", "texto": respuesta})

# --- Pestaña 3: datos y memoria de largo plazo -------------------------------
with tab_datos:
    st.subheader("Solicitudes")
    st.dataframe(leer_tabla("SELECT * FROM solicitudes"), width="stretch", hide_index=True)
    st.subheader("Historial de decisiones (memoria de largo plazo)")
    st.dataframe(leer_tabla("SELECT * FROM historial ORDER BY id DESC"),
                 width="stretch", hide_index=True)
    st.subheader("Notificaciones enviadas (simuladas)")
    st.dataframe(leer_tabla("SELECT * FROM notificaciones ORDER BY id DESC"),
                 width="stretch", hide_index=True)