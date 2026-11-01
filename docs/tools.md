# Herramientas (tools) del agente

Todas están en `agent/tools/`, usan `@tool` de LangChain y tienen docstring
(es lo que el LLM lee para saber cuándo usarlas).

| Tool | Tipo | Entrada | Salida | ¿La puede usar el LLM? |
|---|---|---|---|---|
| consultar_solicitud | Consulta | solicitud_id | dict con la solicitud | Sí |
| consultar_alumno | Consulta (+ memoria) | alumno_id | dict con datos, historial y n.° de justificaciones del semestre | Sí |
| validar_plazo | Razonamiento | solicitud_id | {en_plazo, dias_desde_evento, plazo_maximo, razon} | Sí |
| buscar_reglamento | Consulta (RAG) | consulta, k | lista de {articulo, texto, fuente} | Sí |
| registrar_decision | Escritura (+ memoria) | solicitud_id, decision, razon | {ok, estado} | No |
| notificar_alumno | Escritura | alumno_id, mensaje | {ok, canal} | No |
| procesar_solicitud_completa | Orquestación | solicitud_id | {accion, regla, razon, articulos} | Sí |

## Por qué el LLM no usa las tools de escritura

Las dos tools que escriben (`registrar_decision` y `notificar_alumno`) solo se
llaman desde `procesar_solicitud` en `agent/core.py`, después de que el planner
decide. El LLM, en el chat, solo puede pedir el flujo completo
(`procesar_solicitud_completa`). Así la decisión siempre pasa por las reglas,
aunque alguien escriba en el chat "aprueba esta solicitud".
