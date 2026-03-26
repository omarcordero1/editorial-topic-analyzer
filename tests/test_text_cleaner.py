"""
tests/test_text_cleaner.py
--------------------------
Tests unitarios para el módulo de limpieza de texto.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.text_cleaner import limpiar_texto, combinar_campos, preparar_corpus


class TestLimpiarTexto:

    def test_texto_normal(self):
        resultado = limpiar_texto("Presidente AMLO firma decreto")
        assert resultado == "presidente amlo firma decreto"

    def test_elimina_acentos(self):
        resultado = limpiar_texto("Política económica México")
        assert "politica" in resultado
        assert "economica" in resultado
        assert "mexico" in resultado

    def test_elimina_urls(self):
        resultado = limpiar_texto("Ver más en https://milenio.com/nota123 hoy")
        assert "http" not in resultado
        assert "milenio" not in resultado

    def test_valor_nulo(self):
        assert limpiar_texto(None) == ""
        assert limpiar_texto(float("nan")) == ""
        assert limpiar_texto("") == ""

    def test_elimina_caracteres_especiales(self):
        resultado = limpiar_texto("¡¿Qué pasó con México?")
        assert "!" not in resultado
        assert "?" not in resultado
        assert "¡" not in resultado

    def test_colapsa_espacios(self):
        resultado = limpiar_texto("texto   con    espacios")
        assert "  " not in resultado


class TestCombinarCampos:

    def test_combinacion_basica(self):
        df = pd.DataFrame({
            "titulo": ["Elecciones 2024"],
            "seccion": ["Política"]
        })
        resultado = combinar_campos(df, ["titulo", "seccion"])
        assert "elecciones 2024" in resultado[0]
        assert "politica" in resultado[0]

    def test_campos_faltantes_raises(self):
        df = pd.DataFrame({"titulo": ["texto"]})
        with pytest.raises(ValueError):
            combinar_campos(df, ["columna_inexistente"])

    def test_manejo_nulos(self):
        df = pd.DataFrame({
            "titulo": ["Nota de economía"],
            "seccion": [None]
        })
        resultado = combinar_campos(df, ["titulo", "seccion"])
        assert resultado[0] != ""


class TestPrepararCorpus:

    def test_añade_columnas(self):
        df = pd.DataFrame({
            "titulo": ["Elecciones 2024", "Liga MX semifinal"],
            "seccion": ["Política", "Deportes"]
        })
        df_resultado = preparar_corpus(df)
        assert "texto_limpio" in df_resultado.columns
        assert "texto_analisis" in df_resultado.columns

    def test_no_modifica_original(self):
        df = pd.DataFrame({
            "titulo": ["Nota política"],
            "seccion": ["Nacional"]
        })
        df_copia = df.copy()
        preparar_corpus(df)
        pd.testing.assert_frame_equal(df, df_copia)
