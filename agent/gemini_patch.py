"""Compatibilidad Gemini 3.x + langchain-google-genai 2.x (LangChain 0.3).

Los modelos Gemini 3 exigen que cada functionCall del historial lleve una
"thought_signature". La versión 2.x de la librería no la reenvía, y Google
responde 400 en la segunda llamada del agente (cuando se devuelve el
resultado de la tool). Este parche agrega la firma comodín documentada por
Google ("skip_thought_signature_validator") a la primera functionCall de cada
turno del modelo. Si la librería ya soporta firmas o el campo no existe, no
hace nada.
"""
from langchain_google_genai import chat_models as _cm

_FIRMA = b"skip_thought_signature_validator"
_original = _cm._parse_chat_history


def _parse_chat_history_con_firma(*args, **kwargs):
    system_instruction, contenidos = _original(*args, **kwargs)
    for contenido in contenidos:
        if contenido.role != "model":
            continue
        for parte in contenido.parts:
            if parte.function_call and parte.function_call.name:
                try:
                    if not parte.thought_signature:
                        parte.thought_signature = _FIRMA
                except AttributeError:
                    pass          # versión sin el campo: nada que hacer
                break             # solo la primera functionCall de cada turno
    return system_instruction, contenidos


if _cm._parse_chat_history is _original:
    _cm._parse_chat_history = _parse_chat_history_con_firma