"""
visualizer.py
-------------
Generación de visualizaciones editoriales con matplotlib/seaborn.
"""

import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

matplotlib.use("Agg")  # Backend sin GUI para entornos de servidor
logger = logging.getLogger(__name__)

COLORES = {
    "primario": "#1a73e8",
    "secundario": "#ea4335",
    "terciario": "#34a853",
    "cuaternario": "#9c27b0",
    "fondo": "#f8f9fa",
}


def configurar_estilo() -> None:
    """Configura el estilo global de matplotlib."""
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.facecolor": COLORES["fondo"],
        "axes.facecolor": "white",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
    })


def grafica_temas(
    df: pd.DataFrame,
    ax: plt.Axes,
    top_n: int = 8
) -> None:
    """Barras horizontales de los temas más frecuentes."""
    data = df["tema"].value_counts().head(top_n)
    data.plot(kind="barh", ax=ax, color=COLORES["primario"], edgecolor="white")
    ax.set_title(f"Top {top_n} Temas Más Frecuentes")
    ax.set_xlabel("Cantidad de notas")
    ax.invert_yaxis()


def grafica_impacto(
    df: pd.DataFrame,
    ax: plt.Axes
) -> None:
    """Barras horizontales por área de impacto."""
    data = df["area_impacto"].value_counts()
    colors = sns.color_palette("Set2", len(data))
    data.plot(kind="barh", ax=ax, color=colors, edgecolor="white")
    ax.set_title("Distribución de Áreas de Impacto")
    ax.set_xlabel("Cantidad de notas")
    ax.invert_yaxis()


def grafica_entidades(
    df: pd.DataFrame,
    ax: plt.Axes,
    top_n: int = 10
) -> None:
    """Barras horizontales de los actores principales más mencionados."""
    data = (
        df[df["personaje_principal"] != "No identificado"]["personaje_principal"]
        .value_counts()
        .head(top_n)
    )
    data.plot(kind="barh", ax=ax, color=COLORES["terciario"], edgecolor="white")
    ax.set_title(f"Top {top_n} Actores Principales")
    ax.set_xlabel("Apariciones")
    ax.invert_yaxis()


def grafica_engagement_por_tema(
    df: pd.DataFrame,
    ax: plt.Axes,
    top_n: int = 8
) -> None:
    """Barras de pageviews promedio por tema."""
    data = (
        df.groupby("tema")["Pv´s"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )
    data.plot(kind="bar", ax=ax, color=COLORES["cuaternario"], edgecolor="white")
    ax.set_title(f"Promedio de PVs por Tema (Top {top_n})")
    ax.set_ylabel("PVs Promedio")
    ax.tick_params(axis="x", rotation=45)


def generar_dashboard(
    df: pd.DataFrame,
    ruta_salida: str = "outputs/analisis_editorial.png",
    dpi: int = 300
) -> str:
    """
    Genera el dashboard completo de análisis editorial (2x2 grid).

    Args:
        df: DataFrame procesado con todas las variables
        ruta_salida: Ruta donde guardar la imagen
        dpi: Resolución de la imagen

    Returns:
        Ruta del archivo generado
    """
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)

    configurar_estilo()
    fig, axes = plt.subplots(2, 2, figsize=(18, 13))
    fig.suptitle(
        "Análisis de Cobertura Editorial — Milenio.com",
        fontsize=16,
        fontweight="bold",
        y=1.01
    )

    grafica_temas(df, axes[0, 0])
    grafica_impacto(df, axes[0, 1])
    grafica_entidades(df, axes[1, 0])
    grafica_engagement_por_tema(df, axes[1, 1])

    plt.tight_layout()
    fig.savefig(ruta_salida, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    logger.info(f"Dashboard guardado en: {ruta_salida}")
    return ruta_salida


def grafica_heatmap_seccion_impacto(
    df: pd.DataFrame,
    ruta_salida: str = "outputs/heatmap_seccion_impacto.png"
) -> str:
    """
    Genera un heatmap de sección × área de impacto.

    Args:
        df: DataFrame procesado
        ruta_salida: Ruta donde guardar la imagen

    Returns:
        Ruta del archivo generado
    """
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)

    pivot = (
        df.groupby(["seccion", "area_impacto"])
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        pivot,
        annot=True,
        fmt="d",
        cmap="Blues",
        linewidths=0.5,
        ax=ax
    )
    ax.set_title("Distribución por Sección × Área de Impacto", fontsize=14, fontweight="bold")
    ax.set_xlabel("Área de Impacto")
    ax.set_ylabel("Sección")
    plt.tight_layout()
    fig.savefig(ruta_salida, dpi=200, bbox_inches="tight")
    plt.close(fig)

    logger.info(f"Heatmap guardado en: {ruta_salida}")
    return ruta_salida
