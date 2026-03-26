"""
config/settings.py
------------------
Configuración centralizada del proyecto.
Carga variables de entorno con fallbacks seguros.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Rutas del proyecto ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# ── Configuración del modelo ─────────────────────────────────────────────────
BERTOPIC_MIN_TOPIC_SIZE = int(os.getenv("BERTOPIC_MIN_TOPIC_SIZE", "30"))
BERTOPIC_TOP_N_WORDS = int(os.getenv("BERTOPIC_TOP_N_WORDS", "10"))
SPACY_MODEL = os.getenv("SPACY_MODEL", "es_core_news_sm")

# ── Umbrales de clasificación de impacto ────────────────────────────────────
PV_CRITICO_ALTO = int(os.getenv("PV_CRITICO_ALTO", "5000"))
PV_ENTRETENIMIENTO_VIRAL = int(os.getenv("PV_ENTRETENIMIENTO_VIRAL", "3000"))
PV_SOCIAL_TENDENCIA = int(os.getenv("PV_SOCIAL_TENDENCIA", "2000"))
PV_GENERAL_DESTACABLE = int(os.getenv("PV_GENERAL_DESTACABLE", "1500"))

# ── Parámetros de exportación ────────────────────────────────────────────────
CSV_ENCODING = os.getenv("CSV_ENCODING", "utf-8-sig")
DASHBOARD_DPI = int(os.getenv("DASHBOARD_DPI", "300"))

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# ── Streamlit app ─────────────────────────────────────────────────────────────
APP_TITLE = "Análisis de Cobertura Editorial"
APP_SUBTITLE = "Extracción de Temas, Entidades y Variables Accionables — Milenio.com"
APP_ICON = "📰"
