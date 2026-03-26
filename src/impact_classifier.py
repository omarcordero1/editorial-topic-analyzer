"""
impact_classifier.py
--------------------
Clasificador de áreas de impacto editorial para redacciones periodísticas.
Combina sección, tema y pageviews para generar segmentación accionable.
"""

import logging
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThresholdsConfig:
    """Configuración de umbrales de pageviews para clasificación de impacto."""
    pv_critico_alto: int = 5000
    pv_entretenimiento_viral: int = 3000
    pv_social_tendencia: int = 2000
    pv_general_destacable: int = 1500


# Configuración por defecto
DEFAULT_THRESHOLDS = ThresholdsConfig()

# Secciones de alto impacto institucional
SECCIONES_CRITICAS = frozenset(["Política", "Policía", "Economía", "Estados"])

# Keywords para clasificación por tema
KEYWORDS_DEPORTES = frozenset(["deportes", "futbol", "juego", "liga", "gol", "partido"])
KEYWORDS_NEGOCIOS = frozenset(["economía", "mercado", "empresa", "bolsa", "inversión", "finanzas"])
KEYWORDS_SOCIAL = frozenset(["comunidad", "sociedad", "cultura", "arte", "educación"])


def clasificar_impacto(
    row: pd.Series,
    thresholds: ThresholdsConfig = DEFAULT_THRESHOLDS
) -> str:
    """
    Clasifica una noticia en su área de impacto editorial.

    Lógica de prioridad:
    1. Sección crítica (Política, Policía, Economía, Estados)
    2. Tema deportivo
    3. Tema de negocios
    4. Tema social/cultural
    5. General

    Args:
        row: Fila del DataFrame con campos 'tema', 'seccion', 'Pv´s'
        thresholds: Umbrales de PVs configurables

    Returns:
        Etiqueta de área de impacto
    """
    tema = str(row.get("tema", "")).lower()
    pv = float(row.get("Pv´s", 0)) if pd.notna(row.get("Pv´s")) else 0.0
    seccion = str(row.get("seccion", ""))

    # Nivel 1: Secciones críticas
    if seccion in SECCIONES_CRITICAS:
        return "CRÍTICO - Alto Impacto" if pv > thresholds.pv_critico_alto else "CRÍTICO - Bajo Impacto"

    # Nivel 2: Deportes
    if any(kw in tema for kw in KEYWORDS_DEPORTES):
        return "ENTRETENIMIENTO - Viral" if pv > thresholds.pv_entretenimiento_viral else "ENTRETENIMIENTO - Nicho"

    # Nivel 3: Negocios
    if any(kw in tema for kw in KEYWORDS_NEGOCIOS):
        return "NEGOCIOS - B2B Focus"

    # Nivel 4: Social/Cultural
    if any(kw in tema for kw in KEYWORDS_SOCIAL):
        return "SOCIAL - Tendencia" if pv > thresholds.pv_social_tendencia else "SOCIAL - Comunidad Local"

    # Nivel 5: General
    return "GENERAL - Destacable" if pv > thresholds.pv_general_destacable else "GENERAL - Regularidad"


def asignar_areas_impacto(
    df: pd.DataFrame,
    thresholds: ThresholdsConfig = DEFAULT_THRESHOLDS
) -> pd.DataFrame:
    """
    Asigna área de impacto a todo el DataFrame.

    Args:
        df: DataFrame con columnas 'tema', 'seccion' y 'Pv´s'
        thresholds: Configuración de umbrales (opcional)

    Returns:
        DataFrame con columna 'area_impacto' añadida
    """
    df = df.copy()

    df["area_impacto"] = df.apply(
        lambda row: clasificar_impacto(row, thresholds), axis=1
    )

    distribucion = df["area_impacto"].value_counts()
    logger.info(f"Áreas de impacto asignadas:\n{distribucion.to_string()}")

    return df


def resumen_impacto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen estadístico por área de impacto.

    Returns:
        DataFrame con métricas por área (conteo, PVs promedio, PVs totales)
    """
    if "area_impacto" not in df.columns:
        raise ValueError("El DataFrame no tiene columna 'area_impacto'. Ejecuta asignar_areas_impacto primero.")

    return (
        df.groupby("area_impacto")
        .agg(
            noticias=("titulo", "count"),
            pv_promedio=("Pv´s", "mean"),
            pv_total=("Pv´s", "sum")
        )
        .sort_values("pv_total", ascending=False)
        .round(0)
    )
