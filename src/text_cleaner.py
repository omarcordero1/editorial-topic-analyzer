"""
text_cleaner.py
---------------
Limpieza y normalización de texto en español para análisis NLP.
"""

import re
import logging
import pandas as pd
from typing import Optional
from unidecode import unidecode

logger = logging.getLogger(__name__)

# Stopwords en español para filtrado básico
STOPWORDS_ES = frozenset([
    "el", "la", "de", "que", "y", "a", "en", "es", "se", "los", "las",
    "del", "por", "con", "un", "una", "os", "fue", "han", "pero", "para",
    "su", "al", "lo", "como", "más", "o", "si", "pero", "sus", "le",
    "ya", "sobre", "este", "cuando", "también", "hasta", "hay", "donde",
    "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les",
    "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto",
    "mi", "antes", "algunos", "qué", "unos", "yo", "otro", "otras"
])


def limpiar_texto(texto: Optional[str]) -> str:
    """
    Limpia y normaliza un texto para análisis NLP.

    Pasos:
    1. Manejo de valores nulos
    2. Conversión a minúsculas
    3. Eliminación de acentos (unidecode)
    4. Eliminación de URLs
    5. Eliminación de caracteres especiales
    6. Colapso de espacios múltiples

    Args:
        texto: String de entrada (puede ser None o NaN)

    Returns:
        Texto limpio como string
    """
    if pd.isna(texto) or texto is None:
        return ""

    texto = str(texto).strip()

    if not texto:
        return ""

    # Minúsculas
    texto = texto.lower()

    # Eliminar acentos
    texto = unidecode(texto)

    # Eliminar URLs
    texto = re.sub(r"http\S+|www\.\S+", "", texto)

    # Eliminar menciones y hashtags
    texto = re.sub(r"[@#]\w+", "", texto)

    # Eliminar caracteres especiales (mantener alfanumérico y espacios)
    texto = re.sub(r"[^a-z0-9\s]", "", texto)

    # Colapsar espacios múltiples
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def combinar_campos(
    df: pd.DataFrame,
    campos: list[str],
    separador: str = " "
) -> pd.Series:
    """
    Combina múltiples columnas de texto en una sola para análisis.

    Args:
        df: DataFrame con los datos
        campos: Lista de nombres de columnas a combinar
        separador: Separador entre campos

    Returns:
        Serie con los textos combinados y limpios
    """
    campos_existentes = [c for c in campos if c in df.columns]

    if not campos_existentes:
        raise ValueError(f"Ninguno de los campos existe en el DataFrame: {campos}")

    combinado = df[campos_existentes[0]].fillna("").astype(str)

    for campo in campos_existentes[1:]:
        combinado = combinado + separador + df[campo].fillna("").astype(str)

    logger.info(f"Campos combinados: {campos_existentes}")

    return combinado.apply(limpiar_texto)


def preparar_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara el DataFrame completo con todos los campos de texto limpios.

    Args:
        df: DataFrame original

    Returns:
        DataFrame con columnas 'texto_limpio' y 'texto_analisis' añadidas
    """
    df = df.copy()

    df["texto_limpio"] = df["titulo"].apply(limpiar_texto)
    df["texto_analisis"] = combinar_campos(df, ["titulo", "seccion"])

    n_vacios = (df["texto_analisis"] == "").sum()
    if n_vacios > 0:
        logger.warning(f"{n_vacios} registros con texto vacío después de limpieza")

    logger.info(f"Corpus preparado: {len(df)} textos listos para análisis")

    return df
