"""
main.py
-------
Pipeline principal de análisis de cobertura editorial.
Modo CLI para ejecución batch sobre archivos Excel o CSV.

Uso:
    python main.py --input data/Base_de_trabajo.xlsx
    python main.py --input data/Base_de_trabajo.xlsx --output outputs/
    python main.py --input data/Base_de_trabajo.xlsx --min-topic-size 20
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from config.settings import (
    BERTOPIC_MIN_TOPIC_SIZE, LOG_LEVEL, LOG_FORMAT, OUTPUTS_DIR
)
from src.data_loader import cargar_dataset, resumen_dataset
from src.text_cleaner import preparar_corpus
from src.topic_modeling import asignar_temas
from src.ner_extractor import asignar_entidades
from src.impact_classifier import asignar_areas_impacto, ThresholdsConfig
from src.recommender import exportar_resultados, calcular_matriz_recomendaciones
from src.visualizer import generar_dashboard

# ── Configuración de logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("outputs/pipeline.log", mode="a"),
    ]
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline de Análisis de Cobertura Editorial — Milenio.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --input data/Base_de_trabajo.xlsx
  python main.py --input data/noticias.csv --min-topic-size 15 --no-viz
        """
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=str,
        help="Ruta al archivo de entrada (.xlsx o .csv)"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(OUTPUTS_DIR),
        type=str,
        help="Directorio de salida (default: outputs/)"
    )
    parser.add_argument(
        "--min-topic-size",
        default=BERTOPIC_MIN_TOPIC_SIZE,
        type=int,
        help=f"Tamaño mínimo de cluster BERTopic (default: {BERTOPIC_MIN_TOPIC_SIZE})"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Omitir generación de visualizaciones"
    )
    return parser.parse_args()


def run_pipeline(
    input_path: str,
    output_dir: str,
    min_topic_size: int = BERTOPIC_MIN_TOPIC_SIZE,
    generar_viz: bool = True
) -> None:
    """
    Ejecuta el pipeline completo de análisis editorial.

    Etapas:
    1. Carga y validación del dataset
    2. Limpieza y preparación del corpus
    3. Modelado de temas (BERTopic)
    4. Extracción de entidades (spaCy NER)
    5. Clasificación de impacto
    6. Generación de visualizaciones
    7. Exportación de resultados

    Args:
        input_path: Ruta al archivo de entrada
        output_dir: Directorio para archivos de salida
        min_topic_size: Parámetro de BERTopic
        generar_viz: Si generar el dashboard visual
    """
    inicio = time.time()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE DE ANÁLISIS EDITORIAL")
    logger.info("=" * 60)

    # Etapa 1: Carga
    logger.info("[1/6] Cargando dataset...")
    df = cargar_dataset(input_path)
    resumen = resumen_dataset(df)
    logger.info(f"     ✓ {resumen['total_noticias']:,} noticias | {resumen['secciones']} secciones")

    # Etapa 2: Limpieza
    logger.info("[2/6] Preparando corpus...")
    df = preparar_corpus(df)

    # Etapa 3: BERTopic
    logger.info("[3/6] Modelando temas con BERTopic...")
    df, topic_model = asignar_temas(df, min_topic_size=min_topic_size)
    n_temas = df["tema"].nunique()
    logger.info(f"     ✓ {n_temas} temas identificados")

    # Etapa 4: NER
    logger.info("[4/6] Extrayendo entidades con spaCy...")
    df = asignar_entidades(df)

    # Etapa 5: Clasificación de impacto
    logger.info("[5/6] Clasificando áreas de impacto...")
    thresholds = ThresholdsConfig()
    df = asignar_areas_impacto(df, thresholds)

    # Etapa 6: Visualizaciones
    if generar_viz:
        logger.info("[6/6] Generando visualizaciones...")
        ruta_dashboard = f"{output_dir}/analisis_editorial.png"
        generar_dashboard(df, ruta_dashboard)

    # Exportación
    logger.info("Exportando resultados...")
    exportar_resultados(
        df,
        ruta_csv=f"{output_dir}/Milenio_Analisis_Completo.csv",
        ruta_recomendaciones=f"{output_dir}/Milenio_Recomendaciones.csv"
    )

    # Resumen final
    elapsed = time.time() - inicio
    logger.info("=" * 60)
    logger.info(f"✅ PIPELINE COMPLETADO en {elapsed:.1f}s")
    logger.info(f"   📊 Noticias procesadas: {len(df):,}")
    logger.info(f"   🔍 Temas encontrados: {n_temas}")
    logger.info(f"   📁 Resultados en: {output_dir}/")
    logger.info("=" * 60)


def main() -> None:
    args = parse_args()

    try:
        run_pipeline(
            input_path=args.input,
            output_dir=args.output,
            min_topic_size=args.min_topic_size,
            generar_viz=not args.no_viz
        )
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrumpido por el usuario")
        sys.exit(0)


if __name__ == "__main__":
    main()
