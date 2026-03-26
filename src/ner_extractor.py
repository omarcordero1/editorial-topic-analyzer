"""
ner_extractor.py
----------------
Extracción de entidades nombradas (NER) con spaCy para corpus en español.
Identifica personajes, organizaciones y lugares en titulares periodísticos.
"""

import logging
from collections import Counter
from typing import Optional
import pandas as pd
import spacy

logger = logging.getLogger(__name__)

# Tipos de entidades de interés periodístico
ETIQUETAS_NER = {"PERSON", "ORG", "MISC", "LOC", "GPE"}

# Entidades genéricas a ignorar (ruido)
ENTIDADES_IGNORAR = frozenset([
    "méxico", "mexico", "cdmx", "estado", "gobierno",
    "congreso", "cámara", "senado", "presidencia"
])

_nlp_cache: Optional[object] = None


def _cargar_modelo() -> object:
    """Carga el modelo spaCy (singleton con caché)."""
    global _nlp_cache
    if _nlp_cache is None:
        logger.info("Cargando modelo spaCy es_core_news_sm...")
        try:
            _nlp_cache = spacy.load("es_core_news_sm")
        except OSError:
            raise RuntimeError(
                "Modelo spaCy no encontrado. Ejecuta:\n"
                "python -m spacy download es_core_news_sm"
            )
    return _nlp_cache


def extraer_entidades(
    texto: Optional[str],
    max_chars: int = 500
) -> str:
    """
    Extrae la entidad principal de un texto (titular periodístico).

    Args:
        texto: Titular de la noticia
        max_chars: Límite de caracteres para procesar (por velocidad)

    Returns:
        Nombre de la entidad principal o "No identificado"
    """
    if pd.isna(texto) or not str(texto).strip() or len(str(texto)) < 5:
        return "No identificado"

    nlp = _cargar_modelo()
    doc = nlp(str(texto)[:max_chars])

    entidades = [
        ent.text.strip()
        for ent in doc.ents
        if ent.label_ in ETIQUETAS_NER
        and ent.text.strip().lower() not in ENTIDADES_IGNORAR
        and len(ent.text.strip()) > 2
    ]

    if not entidades:
        return "No identificado"

    # La entidad más frecuente = la más importante del titular
    principal = Counter(entidades).most_common(1)[0][0]
    return principal


def extraer_todas_entidades(
    texto: Optional[str],
    max_chars: int = 500
) -> list[str]:
    """
    Extrae todas las entidades encontradas en un texto.

    Returns:
        Lista de entidades encontradas (puede ser vacía)
    """
    if pd.isna(texto) or not str(texto).strip():
        return []

    nlp = _cargar_modelo()
    doc = nlp(str(texto)[:max_chars])

    return [
        ent.text.strip()
        for ent in doc.ents
        if ent.label_ in ETIQUETAS_NER
        and len(ent.text.strip()) > 2
    ]


def asignar_entidades(
    df: pd.DataFrame,
    columna: str = "titulo"
) -> pd.DataFrame:
    """
    Asigna entidades a todo el DataFrame.

    Args:
        df: DataFrame con titulares
        columna: Columna de texto a procesar

    Returns:
        DataFrame con columna 'personaje_principal' añadida
    """
    df = df.copy()

    logger.info(f"Extrayendo entidades de {len(df)} titulares...")
    df["personaje_principal"] = df[columna].apply(extraer_entidades)

    n_identificados = (df["personaje_principal"] != "No identificado").sum()
    pct = n_identificados / len(df) * 100

    logger.info(f"Entidades extraídas: {n_identificados}/{len(df)} ({pct:.1f}%)")

    return df


def top_entidades(df: pd.DataFrame, n: int = 20) -> pd.Series:
    """
    Retorna el ranking de entidades más mencionadas.

    Args:
        df: DataFrame con columna 'personaje_principal'
        n: Número de entidades a retornar

    Returns:
        Serie con conteo de menciones
    """
    return (
        df[df["personaje_principal"] != "No identificado"]["personaje_principal"]
        .value_counts()
        .head(n)
    )
