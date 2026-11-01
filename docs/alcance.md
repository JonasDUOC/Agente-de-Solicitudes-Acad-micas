# Alcance del Agente de Solicitudes Académicas

## Contexto
Instituto ficticio "Instituto Tecnológico Andino". La coordinación académica
recibe solicitudes de estudiantes que hoy se revisan a mano.

## Lo que SÍ hace
- Atiende dos tipos de solicitud: justificación de inasistencia y prórroga de entrega.
- Consulta los datos del estudiante y su historial de solicitudes.
- Verifica si la solicitud está dentro del plazo del reglamento.
- Busca en el reglamento la regla que aplica y la cita al justificar.
- Aplica 6 reglas de decisión en orden de prioridad.
- Registra la decisión y notifica al estudiante (simulado).
- Recuerda las solicitudes anteriores del estudiante entre sesiones.
- Deriva a un humano los casos que requieren criterio.

## Lo que NO hace
- No rechaza solicitudes por sí solo: cuando corresponde rechazar,
  deriva a coordinación con una recomendación.
- No modifica notas ni asistencia.
- No se conecta a sistemas reales del instituto (datos ficticios).
- No valida la autenticidad de certificados médicos.
- No procesa datos personales reales.

## Métricas de éxito (demo)
- Una solicitud estándar se resuelve en menos de 30 segundos.
- 4 escenarios distintos demostrables en 10 minutos.
- Cada decisión muestra su razón y la regla del reglamento que aplica.