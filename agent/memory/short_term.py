"""Memoria de corto plazo: el hilo de la conversación actual.

Vive en RAM. En Streamlit se guarda en st.session_state para que no se
borre cada vez que la página se recarga. Al cerrar la sesión, se pierde.
Sirve para que el agente entienda preguntas como "¿y por qué?" refiriéndose
a lo que se habló antes.
"""
from langchain.memory import ConversationBufferMemory


def crear_memoria_corto_plazo() -> ConversationBufferMemory:
    """Crea una memoria de conversación en RAM para el agente conversacional."""
    return ConversationBufferMemory(
        memory_key="chat_history",  # nombre del hueco en el prompt (core.py)
        return_messages=True,       # guarda mensajes, no un texto plano
        input_key="input",
        output_key="output",
    )
