"""Indexa data/reglamento.md en Chroma (un fragmento por artículo).

Ejecutar desde la raíz:  python -m scripts.index_reglamento
La primera vez descarga el modelo de embeddings (~450 MB). Ocurre una sola vez.
"""
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document

from agent.memory.semantic import COLECCION_REGLAMENTO, get_embeddings
from config.settings import CHROMA_DIR, REGLAMENTO_PATH


def cargar_fragmentos() -> list[Document]:
    """Divide el reglamento en chunks: uno por cada sección '## Artículo ...'."""
    texto = REGLAMENTO_PATH.read_text(encoding="utf-8")
    secciones = texto.split("\n## ")[1:]  # [0] es el título y la introducción
    docs = []
    for seccion in secciones:
        titulo, _, cuerpo = seccion.partition("\n")
        docs.append(Document(
            page_content=f"{titulo}. {cuerpo.strip()}",
            metadata={"fuente": "reglamento.md", "articulo": titulo.strip()},
        ))
    return docs


def main() -> None:
    docs = cargar_fragmentos()
    if CHROMA_DIR.exists():          # reindexar desde cero, sin duplicados
        shutil.rmtree(CHROMA_DIR)
    Chroma.from_documents(
        docs,
        get_embeddings(),
        collection_name=COLECCION_REGLAMENTO,
        persist_directory=str(CHROMA_DIR),
    )
    print(f"[OK] Indexados {len(docs)} artículos del reglamento en {CHROMA_DIR}")


if __name__ == "__main__":
    main()
