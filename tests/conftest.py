"""Fixtures compartidas por todos los tests.

Antes de CADA test se recrea la base de datos desde los CSV. Así cada test
parte del mismo estado inicial y no depende de lo que hizo el test anterior
(por ejemplo, del historial que guardó la memoria de largo plazo).
"""
import pytest

from config.settings import CHROMA_DIR, DATA_DIR
from scripts import generate_mock_data, seed_data


@pytest.fixture(autouse=True)
def base_de_datos_limpia():
    if not (DATA_DIR / "solicitudes.csv").exists():
        generate_mock_data.main()
    seed_data.main()


# Marca para los tests que necesitan el índice de Chroma ya creado
requiere_chroma = pytest.mark.skipif(
    not CHROMA_DIR.exists(),
    reason="Falta el índice: ejecuta python -m scripts.index_reglamento",
)
