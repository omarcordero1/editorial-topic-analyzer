"""
topic_modeling.py
-----------------
Modelado de temas con BERTopic para corpus editoriales en español.
Extrae clusters semánticos de coberturas periodísticas.
"""

import logging
from typing import Optional
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)

# Stopwords extendidas para BERTopic en español
STOPWORDS_BERTOPIC = [
    "el", "la", "de", "que", "y", "a", "en", "es", "se", "los", "las",
    "del", "por", "con", "un", "una", "os", "fue", "han", "pero", "para",
    "su", "al", "lo", "como", "más", "sobre", "este", "cuando", "también",
    "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante"
]


def construir_modelo(
    min_topic_size: int = 30,
    top_n_words: int = 10,
    nr_topics: Optional[int] = None
) -> BERTopic:
    """
    Construye y configura un modelo BERTopic optimizado para español.

    Args:
        min_topic_size: Tamaño mínimo por cluster (default: 30)
        top_n_words: Palabras representativas por tema (default: 10)
        nr_topics: Número fijo de temas (None = automático)

    Returns:
        Instancia de BERTopic configurada
    """
    vectorizer_model = CountVectorizer(
        max_df=0.95,
        min_df=2,
        stop_words=STOPWORDS_BERTOPIC,
        ngram_range=(1, 2)
    )

    topic_model = BERTopic(
        language="spanish",
        vectorizer_model=vectorizer_model,
        top_n_words=top_n_words,
        min_topic_size=min_topic_size,
        nr_topics=nr_topics,
        verbose=False
    )

    logger.info("Modelo BERTopic construido")
    return topic_model


def entrenar_modelo(
    textos: list[str],
    min_topic_size: int = 30
) -> tuple[BERTopic, list[int], list[float]]:
    """
    Entrena BERTopic sobre el corpus editorial.

    Args:
        textos: Lista de textos limpios
        min_topic_size: Tamaño mínimo por cluster

    Returns:
        Tupla (modelo, topics, probabilidades)
    """
    logger.info(f"Entrenando BERTopic sobre {len(textos)} textos...")

    topic_model = construir_modelo(min_topic_size=min_topic_size)
    topics, probs = topic_model.fit_transform(textos)

    n_topics = len(set(topics)) - (1 if -1 in topics else 0)
    n_outliers = sum(1 for t in topics if t == -1)

    logger.info(f"Temas identificados: {n_topics} clusters | Outliers: {n_outliers}")

    return topic_model, topics, probs


def generar_etiquetas(topic_model: BERTopic, topics: list[int]) -> dict[int, str]:
    """
    Genera etiquetas legibles para cada tema identificado.

    Args:
        topic_model: Modelo BERTopic entrenado
        topics: Lista de IDs de temas

    Returns:
        Diccionario {topic_id: "palabra1 + palabra2 + palabra3"}
    """
    tema_labels = {}

    for topic_id in set(topics):
        if topic_id == -1:
            continue
        words = topic_model.get_topic(topic_id)
        if words:
            top_words = [word for word, _ in words[:3]]
            tema_labels[topic_id] = " + ".join(top_words)

    return tema_labels


def asignar_temas(
    df: pd.DataFrame,
    columna_texto: str = "texto_analisis",
    min_topic_size: int = 30
) -> pd.DataFrame:
    """
    Pipeline completo: entrena BERTopic y asigna temas al DataFrame.

    Args:
        df: DataFrame con textos preparados
        columna_texto: Columna a usar para el análisis
        min_topic_size: Tamaño mínimo por cluster

    Returns:
        DataFrame con columnas 'tema_id', 'tema_probabilidad' y 'tema'
    """
    df = df.copy()
    textos = df[columna_texto].tolist()

    topic_model, topics, probs = entrenar_modelo(textos, min_topic_size)

    df["tema_id"] = topics
    df["tema_probabilidad"] = probs

    tema_labels = generar_etiquetas(topic_model, topics)
    df["tema"] = df["tema_id"].map(tema_labels).fillna("Otro")

    logger.info("Temas asignados al DataFrame exitosamente")

    return df, topic_model
