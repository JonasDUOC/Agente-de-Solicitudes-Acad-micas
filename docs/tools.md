# Herramientas (tools) del agente

| Tool | Tipo | Entrada | Salida |
|---|---|---|---|
| consultar_solicitud | Consulta | solicitud_id | dict con la solicitud |
| consultar_alumno | Consulta | alumno_id | dict con datos + historial |
| validar_plazo | Razonamiento | solicitud_id | {en_plazo, dias, razon} |
| buscar_reglamento | Consulta (RAG) | texto | lista de fragmentos con fuente |
| registrar_decision | Escritura | solicitud_id, estado, nota | {ok} |
| notificar_alumno | Escritura | alumno_id, mensaje | {ok, canal} |