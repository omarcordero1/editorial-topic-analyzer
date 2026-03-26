"""
recommender.py
--------------
Generador de matriz de recomendaciones editoriales.
Produce insights accionables para redacciones periodísticas.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def generar_recomendacion(
    tema: str,
    engagement_promedio: float,
    personaje_principal: str,
    umbral_pv: float
) -> str:
    """
    Genera una recomendación editorial basada en el rendimiento del tema.

    Args:
        tema: Nombre del cluster temático
        engagement_promedio: PVs promedio del tema
        personaje_principal: Entidad más frecuente en el tema
        umbral_pv: PV promedio global como referencia

    Returns:
        Texto de recomendación accionable
    """
    if engagement_promedio > umbral_pv * 1.5:
        return f"🔥 PRIORIZAR: '{tema}' — especialmente cobertura de {personaje_principal}"
    elif engagement_promedio > umbral_pv:
        return f"📈 PROFUNDIZAR: '{tema}' — ángulos con {personaje_principal}"
    elif engagement_promedio > umbral_pv * 0.5:
        return f"👁️ MONITOREAR: '{tema}' — potencial si se activa {personaje_principal}"
    else:
        return f"⚠️ REDUCIR: '{tema}' — bajo rendimiento histórico"


def calcular_matriz_recomendaciones(
    df: pd.DataFrame,
    top_n: int = 15
) -> pd.DataFrame:
    """
    Calcula la matriz completa de recomendaciones editoriales.

    Combina frecuencia de publicación, engagement promedio y entidades
    para generar recomendaciones priorizadas para la redacción.

    Args:
        df: DataFrame con columnas 'tema', 'Pv´s', 'personaje_principal'
        top_n: Número de temas a incluir

    Returns:
        DataFrame con matriz de recomendaciones ordenada por engagement
    """
    requeridas = ["tema", "Pv´s", "personaje_principal"]
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes para recomendaciones: {faltantes}")

    umbral_global = df["Pv´s"].mean()

    temas_top = df["tema"].value_counts().head(top_n).index.tolist()
    df_filtrado = df[df["tema"].isin(temas_top)]

    resumen = (
        df_filtrado.groupby("tema")
        .agg(
            frecuencia=("titulo", "count"),
            engagement_promedio=("Pv´s", "mean"),
            engagement_total=("Pv´s", "sum"),
            personaje_principal=("personaje_principal", lambda x: x.mode().iloc[0] if len(x) > 0 else "N/A")
        )
        .reset_index()
        .sort_values("engagement_promedio", ascending=False)
    )

    resumen["recomendacion"] = resumen.apply(
        lambda row: generar_recomendacion(
            row["tema"],
            row["engagement_promedio"],
            row["personaje_principal"],
            umbral_global
        ),
        axis=1
    )

    resumen["engagement_promedio"] = resumen["engagement_promedio"].round(0).astype(int)
    resumen["engagement_total"] = resumen["engagement_total"].round(0).astype(int)

    logger.info(f"Matriz generada: {len(resumen)} temas evaluados")

    return resumen


def exportar_resultados(
    df: pd.DataFrame,
    ruta_csv: str = "outputs/Milenio_Analisis_Completo.csv",
    ruta_recomendaciones: str = "outputs/Milenio_Recomendaciones.csv"
) -> None:
    """
    Exporta el DataFrame procesado y las recomendaciones a CSV.

    Args:
        df: DataFrame con todos los campos procesados
        ruta_csv: Ruta de salida para el análisis completo
        ruta_recomendaciones: Ruta de salida para las recomendaciones
    """
    import os
    os.makedirs("outputs", exist_ok=True)

    columnas_salida = [
        col for col in [
            "id", "titulo", "URL", "editor", "plaza", "Fecha",
            "tema", "tema_probabilidad", "personaje_principal",
            "area_impacto", "Pv´s", "seccion"
        ]
        if col in df.columns
    ]

    df[columnas_salida].to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    logger.info(f"Análisis completo exportado: {ruta_csv}")

    if "tema" in df.columns and "personaje_principal" in df.columns:
        recomendaciones = calcular_matriz_recomendaciones(df)
        recomendaciones.to_csv(ruta_recomendaciones, index=False, encoding="utf-8-sig")
        logger.info(f"Recomendaciones exportadas: {ruta_recomendaciones}")
