"""Tool (consulta, RAG): busca en el reglamento por significado."""
from langchain_core.tools import tool

from agent.memory.semantic import get_vectorstore


@tool
def buscar_reglamento(consulta: str, k: int = 2) -> list[dict]:
    """Busca en el reglamento académico los artículos más relacionados con la consulta.

    Úsala para justificar una decisión o responder dudas sobre plazos,
    justificaciones, prórrogas, documentos de respaldo o límites por semestre.
    Devuelve una lista de fragmentos con 'articulo', 'texto' y 'fuente'.
    """
    try:
        resultados = get_vectorstore().similarity_search(consulta, k=k)
    except Exception as e:  # p. ej., no se ejecutó scripts.index_reglamento
        return [{"error": f"No se pudo consultar el reglamento: {e}"}]
    return [
        {"articulo": d.metadata.get("articulo", ""),
         "texto": d.page_content,
         "fuente": d.metadata.get("fuente", "reglamento.md")}
        for d in resultados
    ]


if __name__ == "__main__":
    for r in buscar_reglamento.invoke({"consulta": "quiero más tiempo para entregar el trabajo"}):
        print("-", r.get("articulo"), "|", r.get("texto", r.get("error"))[:90])
