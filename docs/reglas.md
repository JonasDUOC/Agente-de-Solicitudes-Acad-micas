# Reglas de decisión (orden de prioridad)

El agente evalúa de arriba hacia abajo y se detiene en la primera que se cumple.

| # | Condición | Acción | Razón |
|---|---|---|---|
| 1 | Fuera de plazo | derivar_coordinacion | Reglamento: plazos. Se recomienda rechazo, decide un humano |
| 2 | Afecta una evaluación o pide más de 7 días de prórroga | derivar_docente | Solo el docente puede reprogramar |
| 3 | 3 o más justificaciones en el semestre | derivar_revision | Seguimiento académico |
| 4 | Falta respaldo (certificado o documento) | solicitar_info | Completitud |
| 5 | Primera solicitud del semestre | aprobar_automatico | Flujo estándar |
| 6 | Caso estándar | aprobar_automatico | Flujo estándar |