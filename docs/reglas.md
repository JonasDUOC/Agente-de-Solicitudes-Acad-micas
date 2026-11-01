# Reglas de decisión (orden de prioridad)

El agente evalúa de arriba hacia abajo y **se detiene en la primera que se cumple**.
Implementadas en `agent/planner.py`. Los números viven en `config/settings.py`
y deben coincidir con `data/reglamento.md`.

| # | Condición | Acción | Razón (artículo del reglamento) |
|---|---|---|---|
| 0 | Tipo de trámite no soportado (ej. retiro de asignatura) | derivar_coordinacion | Fuera del alcance del agente (Art. 7) |
| 1 | Presentada más de 5 días después del evento | derivar_coordinacion | Fuera de plazo. Se recomienda rechazo, decide un humano (Art. 1 y 6) |
| 2 | Afecta una evaluación, o pide más de 7 días de prórroga | derivar_docente | Solo el docente puede reprogramar (Art. 2 y 3) |
| 3 | Sería la 3.ª justificación (o más) del alumno en el semestre | derivar_revision | Seguimiento académico (Art. 4). Usa la memoria de largo plazo |
| 4 | Falta documento de respaldo | solicitar_info | Completitud (Art. 5) |
| 5 | Caso estándar | aprobar_automatico | Cumple todos los requisitos |

## Ejemplo de prioridad

Prórroga de 10 días, presentada fuera de plazo y sin respaldo: cumple las reglas
1, 2 y 4, pero se activa **solo la 1** (`derivar_coordinacion`), porque es la
primera que se cumple. No tiene sentido pedir un documento si la solicitud
igual está fuera de plazo.
