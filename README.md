# Agente de Solicitudes Académicas

Agente de IA que revisa solicitudes de estudiantes (justificaciones de
inasistencia y prórrogas de entrega) para la coordinación académica de una
institución **ficticia**. Consulta los datos, recuerda el historial de cada
alumno, decide con reglas priorizadas, cita el reglamento y deriva a un humano
los casos que requieren criterio.

Proyecto de la Evaluación Parcial N°2 de ISY0101 – Ingeniería de Soluciones con IA (DuocUC).

## Problema

La coordinación revisa estas solicitudes a mano: es lento en los peaks del
semestre, las decisiones varían entre funcionarios y queda poca trazabilidad.
El agente resuelve los casos simples en segundos, deja registro de cada
decisión con su fundamento y deriva los delicados. El humano sigue a cargo:
**el agente nunca rechaza por sí solo**.

## Arquitectura

```
app.py  ->  agent/core.py  ->  planner.py / tools/ / memory/  ->  config/ + data/
```

| Componente | Uso |
|---|---|
| LangChain | Tools (`@tool`), agente conversacional (`AgentExecutor`), memoria |
| Gemini (modelo en `LLM_MODEL`) | LLM del chat |
| SQLite | Datos mock + memoria de largo plazo (tabla `historial`) |
| Chroma + sentence-transformers | Búsqueda semántica en el reglamento (RAG) |
| Streamlit | Interfaz de la demo |
| pytest | Pruebas automatizadas |

Diagramas de orquestación: [docs/diagrama_orquestacion.md](docs/diagrama_orquestacion.md)

### Flujo híbrido

- **Procesar solicitud** (`procesar_solicitud`): siempre la misma secuencia de
  7 pasos y un planner con reglas en código. Es determinista, trazable y no
  depende del LLM.
- **Chat** (`crear_agente`): Gemini elige qué tools usar para responder
  preguntas abiertas. Solo tiene tools de lectura; para resolver una solicitud
  debe pasar por el flujo completo, así que no puede saltarse las reglas.

### Memoria

| Tipo | Dónde | Para qué |
|---|---|---|
| Corto plazo | `ConversationBufferMemory` en `st.session_state` | El chat recuerda lo que se habló ("¿y por qué?") |
| Largo plazo | Tabla `historial` en SQLite | Recuerda decisiones anteriores entre sesiones; la regla 3 la usa |
| Semántica | Chroma con `data/reglamento.md` | Encuentra el artículo por significado, no por palabra exacta |

### Tools

Ver [docs/tools.md](docs/tools.md). Reglas de decisión: [docs/reglas.md](docs/reglas.md).
Alcance: [docs/alcance.md](docs/alcance.md).

## Instalación

Requisitos: Python 3.10 a 3.13 (LangChain 0.3 no es compatible con 3.14), Git y una API key gratuita de Gemini
(https://aistudio.google.com/apikey).

```bash
git clone https://github.com/JonasDUOC/Agente-de-Solicitudes-Acad-micas.git
cd Agente-de-Solicitudes-Acad-micas
python -m venv .venv
```

Activar el entorno virtual:

```bash
.venv\Scripts\Activate.ps1      # Windows (PowerShell)
source .venv/bin/activate       # Mac / Linux
```

Instalar dependencias y configurar la key:

```bash
pip install -r requirements.txt
cp .env.example .env            # luego abrir .env y pegar la API key
```

Preparar datos e índice (ejecutar **desde la raíz** del proyecto, con `-m`):

```bash
python scripts/verify_llm.py            # debe imprimir "Hola desde Gemini"
python -m scripts.generate_mock_data    # crea data/alumnos.csv y data/solicitudes.csv
python -m scripts.seed_data             # crea data/academico.db
python -m scripts.index_reglamento      # crea data/chroma_db/ (1.ª vez descarga el modelo)
```

Probar y ejecutar:

```bash
pytest tests/ -v
streamlit run app.py                    # abre http://localhost:8501
```

## Uso: escenarios de la demo

En la pestaña **Procesar solicitud**:

| Solicitud | Caso | Resultado esperado |
|---|---|---|
| SOL-001 | Justificación con certificado, en plazo | `aprobar_automatico` (regla 5) |
| SOL-002 | Prórroga de 10 días, fuera de plazo, sin respaldo | `derivar_coordinacion` (regla 1) |
| SOL-003 | Inasistencia en día de prueba | `derivar_docente` (regla 2) |
| SOL-004 | Prórroga de 10 días | `derivar_docente` (regla 2) |
| SOL-005 | Justificación sin documento | `solicitar_info` (regla 4) |
| SOL-007 | Retiro de asignatura | `derivar_coordinacion` (regla 0) |
| SOL-008, 009, 010 | Mismo alumno, tres justificaciones | aprobar, aprobar, `derivar_revision` (regla 3, memoria) |

Para repetir la demo: botón **Reiniciar datos de demo** (o `python -m scripts.seed_data`).

En la pestaña **Chat**: "¿Cuántos días tengo para presentar una justificación?",
"Revisa la SOL-006", "Procésala", "¿Y por qué?".

## Estructura

```
config/settings.py      rutas, umbrales de las reglas, modelo
data/reglamento.md      reglamento ficticio (fuente del RAG)
agent/core.py           orquestador (flujo determinista + agente LLM)
agent/planner.py        reglas de decisión por prioridad
agent/tools/            6 tools
agent/memory/           memoria de corto, largo plazo y semántica
scripts/                generación de datos, carga en SQLite, indexación
tests/                  pruebas (tools, planner, end-to-end)
docs/                   alcance, tools, reglas, diagramas
evidence/               capturas y salida de pytest
app.py                  interfaz Streamlit
```

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `No module named 'config'` | Ejecutar desde la raíz con `python -m scripts.xxx` |
| `no such table` | `python -m scripts.seed_data` |
| El RAG muestra "No se pudo consultar el reglamento" | `python -m scripts.index_reglamento` |
| Error 404 del modelo | Cambiar `LLM_MODEL` en `.env` por un modelo vigente |
| Error 429 en el chat | Cuota gratuita agotada: la pestaña Procesar sigue funcionando sin LLM |
| "La solicitud ya fue procesada" | Botón Reiniciar datos de demo |

## Declaración de uso de IA

| Herramienta | Uso | Validado por |
|---|---|---|
| Gemini | Motor del agente conversacional | Equipo |
| Claude (Anthropic) | Tutoría, apoyo en código y estructura del README | [completar] |

## Referencias

[completar en formato APA: LangChain, Chroma, Gemini API, Streamlit, sentence-transformers, material del curso]
