"""
tests/test_impact_classifier.py
--------------------------------
Tests unitarios para el clasificador de impacto editorial.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.impact_classifier import clasificar_impacto, asignar_areas_impacto, ThresholdsConfig


class TestClasificarImpacto:

    def setup_method(self):
        """Umbrales de test predecibles."""
        self.thresholds = ThresholdsConfig(
            pv_critico_alto=5000,
            pv_entretenimiento_viral=3000,
            pv_social_tendencia=2000,
            pv_general_destacable=1500
        )

    def _fila(self, tema="general", seccion="Nacional", pvs=1000):
        return pd.Series({"tema": tema, "seccion": seccion, "Pv´s": pvs})

    def test_critico_alto_impacto(self):
        fila = self._fila(seccion="Política", pvs=10000)
        assert "CRÍTICO - Alto Impacto" == clasificar_impacto(fila, self.thresholds)

    def test_critico_bajo_impacto(self):
        fila = self._fila(seccion="Política", pvs=100)
        assert "CRÍTICO - Bajo Impacto" == clasificar_impacto(fila, self.thresholds)

    def test_entretenimiento_viral(self):
        fila = self._fila(tema="futbol liga mx", seccion="Deportes", pvs=5000)
        assert "ENTRETENIMIENTO - Viral" == clasificar_impacto(fila, self.thresholds)

    def test_entretenimiento_nicho(self):
        fila = self._fila(tema="futbol liga mx", seccion="Deportes", pvs=500)
        assert "ENTRETENIMIENTO - Nicho" == clasificar_impacto(fila, self.thresholds)

    def test_general_destacable(self):
        fila = self._fila(pvs=2000)
        assert "GENERAL - Destacable" == clasificar_impacto(fila, self.thresholds)

    def test_general_regularidad(self):
        fila = self._fila(pvs=500)
        assert "GENERAL - Regularidad" == clasificar_impacto(fila, self.thresholds)

    def test_pv_nulo_no_explota(self):
        fila = pd.Series({"tema": "general", "seccion": "Nacional", "Pv´s": None})
        resultado = clasificar_impacto(fila, self.thresholds)
        assert isinstance(resultado, str)


class TestAsignarAreasImpacto:

    def test_añade_columna(self):
        df = pd.DataFrame({
            "titulo": ["Nota A", "Nota B"],
            "tema": ["política nacional", "futbol"],
            "seccion": ["Política", "Deportes"],
            "Pv´s": [8000, 500]
        })
        df_resultado = asignar_areas_impacto(df)
        assert "area_impacto" in df_resultado.columns

    def test_no_nulos(self):
        df = pd.DataFrame({
            "titulo": ["A", "B", "C"],
            "tema": ["general", "economía mercado", "deportes futbol"],
            "seccion": ["Nacional", "Economía", "Deportes"],
            "Pv´s": [100, 200, 300]
        })
        df_resultado = asignar_areas_impacto(df)
        assert df_resultado["area_impacto"].notna().all()

    def test_valores_validos(self):
        df = pd.DataFrame({
            "titulo": ["A"],
            "tema": ["política"],
            "seccion": ["Nacional"],
            "Pv´s": [1000]
        })
        df_resultado = asignar_areas_impacto(df)
        areas_validas = {
            "CRÍTICO - Alto Impacto", "CRÍTICO - Bajo Impacto",
            "ENTRETENIMIENTO - Viral", "ENTRETENIMIENTO - Nicho",
            "NEGOCIOS - B2B Focus",
            "SOCIAL - Tendencia", "SOCIAL - Comunidad Local",
            "GENERAL - Destacable", "GENERAL - Regularidad"
        }
        assert df_resultado["area_impacto"].iloc[0] in areas_validas
