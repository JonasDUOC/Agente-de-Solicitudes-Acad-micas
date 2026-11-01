# Alcance del Agente de Solicitudes Académicas

## Contexto
Institución ficticia ("Instituto de Educación Superior"). La coordinación
académica recibe solicitudes de estudiantes que hoy se revisan a mano: es lento
en los peaks del semestre, inconsistente entre funcionarios y deja poca
trazabilidad.

## Lo que SÍ hace
- Atiende dos tipos de solicitud: justificación de inasistencia y prórroga de entrega.
- Consulta los datos del estudiante y su historial de solicitudes.
- Verifica si la solicitud se presentó dentro del plazo del reglamento (5 días).
- Busca en el reglamento el artículo que aplica y lo cita al justificar (RAG).
- Aplica reglas de decisión en orden de prioridad (ver reglas.md).
- Registra la decisión y notifica al estudiante (simulado).
- Recuerda las decisiones anteriores de cada estudiante entre sesiones.
- Responde preguntas en lenguaje natural sobre solicitudes y reglamento (chat con Gemini).
- Deriva a un humano los casos que requieren criterio.

## Lo que NO hace
- No rechaza solicitudes por sí solo: cuando corresponde rechazar,
  deriva a coordinación con una recomendación.
- No procesa otros tipos de solicitud (por ejemplo, retiro de asignatura):
  las deriva a coordinación sin evaluarlas.
- No modifica notas ni asistencia.
- No se conecta a sistemas reales de una institución (datos ficticios).
- No valida la autenticidad de certificados médicos.
- No procesa datos personales reales.

## Métricas de éxito (demo)
- Una solicitud estándar se resuelve en menos de 30 segundos.
- Al menos 4 escenarios distintos demostrables en 10 minutos.
- Cada decisión muestra su razón, la regla que se activó y el artículo del reglamento.
