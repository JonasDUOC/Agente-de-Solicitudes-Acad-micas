"""Memoria semántica: acceso a Chroma (base de datos vectorial).

La usan dos piezas:
- scripts/index_reglamento.py, que ESCRIBE el índice (una vez).
- la tool buscar_reglamento, que LEE el índice (en cada búsqueda).
"""
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from config.settings import CHROMA_DIR, EMBEDDINGS_MODEL

COLECCION_REGLAMENTO = "reglamento"


@lru_cache(maxsize=1)
def get_embeddings():
    """Carga el modelo de embeddings una sola vez (es lento de cargar)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)


def get_vectorstore() -> Chroma:
    """Abre la colección del reglamento guardada en data/chroma_db/."""
    return Chroma(
        collection_name=COLECCION_REGLAMENTO,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )
