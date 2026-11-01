# Diagrama de orquestación del agente

## 1. Componentes y capas

```mermaid
flowchart TD
    U["Usuario (funcionario)<br/>Streamlit app.py"]

    U -->|"Pestaña Procesar"| PS["procesar_solicitud<br/>flujo determinista"]
    U -->|"Pestaña Chat"| AG["Agente LLM<br/>AgentExecutor + Gemini"]
    AG -->|"elige tools de lectura"| TL
    AG -->|"para resolver"| PS
    MC[("Memoria corto plazo<br/>ConversationBufferMemory")] <--> AG

    subgraph TL["Tools (agent/tools)"]
        T1["consultar_solicitud"]
        T2["consultar_alumno"]
        T3["validar_plazo"]
        T4["buscar_reglamento"]
        T5["registrar_decision"]
        T6["notificar_alumno"]
    end

    PS --> T1 & T2 & T3
    PS --> PL{"Planner<br/>reglas 0 a 5"}
    PL --> T4
    PL --> T5 & T6

    T1 & T3 --> DB[("SQLite<br/>solicitudes y alumnos")]
    T2 <--> ML[("Memoria largo plazo<br/>tabla historial")]
    T5 --> ML
    T4 --> CH[("Memoria semántica<br/>Chroma: reglamento.md")]

    style PL fill:#ffe1b3
    style AG fill:#b3d9ff
```

## 2. Flujo de una solicitud (procesar_solicitud)

```mermaid
flowchart TD
    A["1. consultar_solicitud"] --> B["2. consultar_alumno<br/>trae historial"]
    B --> C["3. validar_plazo"]
    C --> D{"4. Planner"}
    D -->|"R0 tipo no soportado"| X1["derivar_coordinacion"]
    D -->|"R1 fuera de plazo"| X1
    D -->|"R2 evaluación o prórroga mayor a 7 días"| X2["derivar_docente"]
    D -->|"R3 tercera justificación"| X3["derivar_revision"]
    D -->|"R4 sin respaldo"| X4["solicitar_info"]
    D -->|"R5 caso estándar"| X5["aprobar_automatico"]
    X1 & X2 & X3 & X4 & X5 --> E["5. buscar_reglamento<br/>cita el artículo"]
    E --> F["6. registrar_decision<br/>guarda en memoria"]
    F --> G["7. notificar_alumno"]
    F -.->|"la próxima solicitud del alumno lee este historial"| B
```

La flecha punteada es la que muestra la memoria: lo que el agente guarda en
el paso 6 cambia lo que decide la próxima vez (regla 3).
