"""Genera datos ficticios: data/alumnos.csv y data/solicitudes.csv.

Ejecutar desde la raíz del proyecto:  python -m scripts.generate_mock_data

Las primeras solicitudes son ESCENARIOS FIJOS para la demo (una por regla).
El resto se genera al azar con semilla fija, así siempre salen iguales.
"""
import csv
import random
from datetime import date, timedelta

from config.settings import DATA_DIR

random.seed(42)  # misma semilla = mismos datos cada vez (demo y tests repetibles)

NOMBRES = [
    "Ana Rojas", "Benjamín Soto", "Camila Fuentes", "Diego Muñoz",
    "Elena Vargas", "Felipe Contreras", "Gabriela Silva", "Hernán Castro",
    "Isidora Pérez", "Joaquín Morales", "Karina Díaz", "Lucas Herrera",
]
CARRERAS = ["Ingeniería en Informática", "Analista Programador",
            "Ingeniería en Conectividad y Redes"]
ASIGNATURAS = ["Programación Back End", "Base de Datos", "Ingeniería de Software",
               "Ingeniería de Soluciones con IA", "Estadística Descriptiva"]

INICIO_SEMESTRE = date(2026, 8, 3)


def fecha(d: date) -> str:
    return d.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Escenarios fijos para la demo. Columnas:
# (alumno, tipo, asignatura, fecha_evento, dias_despues, dias_solicitados,
#  afecta_evaluacion, tiene_respaldo, descripcion)
# dias_despues = cuántos días después del evento se presentó la solicitud.
# ---------------------------------------------------------------------------
ESCENARIOS = [
    # SOL-001 -> regla 5: caso estándar, se aprueba solo
    ("ALU-001", "justificacion_inasistencia", "Base de Datos", date(2026, 10, 20), 2, 0,
     False, True, "Estuve con fiebre y adjunto certificado médico."),
    # SOL-002 -> regla 1: fuera de plazo (aunque también pide >7 días y no tiene respaldo)
    ("ALU-002", "prorroga_entrega", "Programación Back End", date(2026, 10, 5), 9, 10,
     False, False, "Necesito más tiempo para terminar el proyecto."),
    # SOL-003 -> regla 2: la inasistencia fue en día de prueba
    ("ALU-003", "justificacion_inasistencia", "Estadística Descriptiva", date(2026, 10, 22), 1, 0,
     True, True, "Falté a la prueba 2 por un trámite médico, adjunto constancia."),
    # SOL-004 -> regla 2: prórroga de más de 7 días
    ("ALU-005", "prorroga_entrega", "Ingeniería de Software", date(2026, 10, 28), -2, 10,
     False, True, "Pido 10 días más porque mi equipo se rompió, adjunto boleta del servicio técnico."),
    # SOL-005 -> regla 4: falta el documento de respaldo
    ("ALU-006", "justificacion_inasistencia", "Base de Datos", date(2026, 10, 23), 3, 0,
     False, False, "Ese día no pude ir por un problema familiar."),
    # SOL-006 -> regla 5: prórroga corta con respaldo
    ("ALU-007", "prorroga_entrega", "Ingeniería de Soluciones con IA", date(2026, 10, 30), -1, 3,
     False, True, "Solicito 3 días de prórroga por licencia médica, adjunto certificado."),
    # SOL-007 -> regla 0: tipo de trámite fuera del alcance del agente
    ("ALU-008", "retiro_asignatura", "Estadística Descriptiva", date(2026, 10, 25), 1, 0,
     False, True, "Quiero retirar la asignatura."),
    # SOL-008, SOL-009, SOL-010 -> memoria (regla 3): mismo alumno, 3 justificaciones.
    # Procesadas en orden: aprobar, aprobar, y la tercera se deriva a revisión.
    ("ALU-004", "justificacion_inasistencia", "Programación Back End", date(2026, 9, 8), 1, 0,
     False, True, "Adjunto certificado médico por gripe."),
    ("ALU-004", "justificacion_inasistencia", "Base de Datos", date(2026, 9, 29), 2, 0,
     False, True, "Adjunto certificado médico, control dental."),
    ("ALU-004", "justificacion_inasistencia", "Ingeniería de Software", date(2026, 10, 27), 1, 0,
     False, True, "Adjunto certificado médico, nuevamente enfermo."),
]

TIPOS_ALEATORIOS = ["justificacion_inasistencia", "prorroga_entrega"]
DESCRIPCIONES = {
    "justificacion_inasistencia": ["Adjunto certificado médico.",
                                   "Tuve un trámite que no podía postergar, adjunto constancia.",
                                   "Problema de transporte, adjunto comprobante."],
    "prorroga_entrega": ["Solicito prórroga por carga de trabajo.",
                         "Necesito unos días más por motivos de salud.",
                         "Mi computador falló, pido extensión."],
}


def generar_alumnos() -> list[list]:
    filas = []
    for i, nombre in enumerate(NOMBRES, start=1):
        usuario = nombre.lower().replace(" ", ".").replace("í", "i").replace("é", "e") \
            .replace("á", "a").replace("ñ", "n")
        filas.append([f"ALU-{i:03d}", nombre, f"{usuario}@alumno.example.cl",
                      random.choice(CARRERAS)])
    return filas


def generar_solicitudes() -> list[list]:
    filas = []
    n = 1
    for (alu, tipo, asig, evento, despues, dias, afecta, respaldo, desc) in ESCENARIOS:
        filas.append([f"SOL-{n:03d}", alu, tipo, asig, fecha(evento),
                      fecha(evento + timedelta(days=despues)), dias,
                      int(afecta), int(respaldo), desc, "pendiente"])
        n += 1

    # Solicitudes extra al azar (alumnos 9 a 12, para no mezclarse con la demo)
    for _ in range(10):
        tipo = random.choice(TIPOS_ALEATORIOS)
        evento = INICIO_SEMESTRE + timedelta(days=random.randint(10, 85))
        despues = random.randint(-3, 7)
        dias = random.randint(1, 10) if tipo == "prorroga_entrega" else 0
        filas.append([f"SOL-{n:03d}", f"ALU-{random.randint(9, 12):03d}", tipo,
                      random.choice(ASIGNATURAS), fecha(evento),
                      fecha(evento + timedelta(days=despues)), dias,
                      int(random.random() < 0.2), int(random.random() < 0.8),
                      random.choice(DESCRIPCIONES[tipo]), "pendiente"])
        n += 1
    return filas


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "alumnos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["alumno_id", "nombre", "email", "carrera"])
        w.writerows(generar_alumnos())

    with open(DATA_DIR / "solicitudes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["solicitud_id", "alumno_id", "tipo", "asignatura", "fecha_evento",
                    "fecha_solicitud", "dias_solicitados", "afecta_evaluacion",
                    "tiene_respaldo", "descripcion", "estado"])
        w.writerows(generar_solicitudes())

    print("[OK] Datos generados en data/ (alumnos.csv y solicitudes.csv)")


if __name__ == "__main__":
    main()
