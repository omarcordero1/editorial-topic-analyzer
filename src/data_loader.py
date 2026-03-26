"""
data_loader.py
--------------
Carga y validación de datasets editoriales.
Soporta Excel (.xlsx) y CSV como fuentes de entrada.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

COLUMNAS_REQUERIDAS = ["titulo", "seccion", "Pv´s"]
COLUMNAS_OPCIONALES = ["id", "URL", "editor", "plaza", "Fecha"]


def cargar_dataset(
    ruta: str,
    max_columnas: int = 16,
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """
    Carga un dataset editorial desde Excel o CSV.

    Args:
        ruta: Ruta al archivo (.xlsx o .csv)
        max_columnas: Límite de columnas a cargar (elimina columnas vacías)
        encoding: Codificación del archivo CSV

    Returns:
        DataFrame limpio y validado

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si faltan columnas requeridas
    """
    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    logger.info(f"Cargando dataset desde: {ruta}")

    if ruta.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(ruta)
    elif ruta.suffix == ".csv":
        df = pd.read_csv(ruta, encoding=encoding)
    else:
        raise ValueError(f"Formato no soportado: {ruta.suffix}. Use .xlsx o .csv")

    # Eliminar columnas vacías
    df = df[df.columns[:max_columnas]]
    df = df.dropna(how="all")

    logger.info(f"Dataset cargado: {df.shape[0]} noticias, {df.shape[1]} columnas")

    _validar_columnas(df)

    return df


def _validar_columnas(df: pd.DataFrame) -> None:
    """Verifica que el DataFrame contiene las columnas mínimas necesarias."""
    columnas_faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]

    if columnas_faltantes:
        raise ValueError(
            f"Columnas requeridas faltantes: {columnas_faltantes}\n"
            f"Columnas disponibles: {df.columns.tolist()}"
        )

    logger.info(f"Validación OK — columnas requeridas presentes")


def resumen_dataset(df: pd.DataFrame) -> dict:
    """
    Genera un resumen estadístico del dataset.

    Returns:
        Diccionario con métricas del dataset
    """
    return {
        "total_noticias": len(df),
        "secciones": df["seccion"].nunique() if "seccion" in df.columns else 0,
        "editores": df["editor"].nunique() if "editor" in df.columns else 0,
        "pv_promedio": df["Pv´s"].mean() if "Pv´s" in df.columns else 0,
        "pv_total": df["Pv´s"].sum() if "Pv´s" in df.columns else 0,
        "columnas": df.columns.tolist(),
    }
