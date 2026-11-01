"""Configuración central del proyecto.

Todos los números de las reglas viven aquí (no repartidos por el código).
Si cambia el reglamento, se cambia el número una sola vez.
OJO: estos valores deben coincidir con lo que dice data/reglamento.md.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env y deja sus valores disponibles en os.getenv

# --- Rutas ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent   # raíz del proyecto
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "academico.db"                  # SQLite (datos + memoria)
CHROMA_DIR = DATA_DIR / "chroma_db"                  # índice vectorial (RAG)
REGLAMENTO_PATH = DATA_DIR / "reglamento.md"

# --- Institución y periodo ----------------------------------------------
NOMBRE_INSTITUCION = "Instituto de Educación Superior (ficticio)"
SEMESTRE_ACTUAL = "2026-2"

# --- Tipos de solicitud que el agente SÍ procesa (alcance) ---------------
TIPOS_SOPORTADOS = ("justificacion_inasistencia", "prorroga_entrega")

# --- Reglas de negocio (deben coincidir con data/reglamento.md) ----------
PLAZO_PRESENTACION_DIAS = 5          # Art. 1: días para presentar la solicitud
MAX_DIAS_PRORROGA_AUTO = 7           # Art. 3: prórroga máxima sin pasar por docente
UMBRAL_JUSTIFICACIONES_SEMESTRE = 3  # Art. 4: desde la 3ª justificación -> revisión

# --- LLM y embeddings -----------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")
# Modelo de embeddings local y gratuito. Es multilingüe porque el reglamento
# está en español (el de la guía, all-MiniLM-L6-v2, está entrenado en inglés).
EMBEDDINGS_MODEL = os.getenv(
    "EMBEDDINGS_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
