"""
app/app.py
----------
Dashboard interactivo de análisis de cobertura editorial.
Construido con Streamlit para exploración por redacciones periodísticas.

Ejecutar:
    streamlit run app/app.py
"""

import io
import logging
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import APP_TITLE, APP_SUBTITLE, APP_ICON
from src.data_loader import cargar_dataset, resumen_dataset
from src.text_cleaner import preparar_corpus
from src.topic_modeling import asignar_temas
from src.ner_extractor import asignar_entidades, top_entidades
from src.impact_classifier import asignar_areas_impacto, resumen_impacto
from src.recommender import calcular_matriz_recomendaciones

logger = logging.getLogger(__name__)

# ─── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Estilos CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        border-left: 4px solid #1a73e8;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1a73e8; }
    .metric-label { font-size: 0.85rem; color: #666; }
    .stAlert { border-radius: 8px; }
    h1 { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Milenio_Logo.svg/320px-Milenio_Logo.svg.png",
             width=160)
    st.markdown("---")
    st.header("⚙️ Configuración")

    archivo = st.file_uploader(
        "📂 Subir dataset editorial",
        type=["xlsx", "csv"],
        help="Formato: columnas título, seccion, Pv´s"
    )

    st.markdown("### Parámetros del modelo")
    min_topic_size = st.slider(
        "Tamaño mínimo de cluster (BERTopic)",
        min_value=5, max_value=100, value=30, step=5,
        help="Mínimo de artículos por tema. Menor = más temas, mayor = menos temas"
    )

    top_n = st.slider(
        "Top N temas a mostrar",
        min_value=5, max_value=20, value=8, step=1
    )

    ejecutar = st.button("🚀 Analizar", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("**📌 Campos requeridos:**")
    st.markdown("- `titulo`\n- `seccion`\n- `Pv´s`")
    st.markdown("**📌 Campos opcionales:**")
    st.markdown("- `id`, `URL`, `editor`, `plaza`, `Fecha`")
    st.markdown("---")
    st.markdown("Desarrollado por [Omar Cordero](https://github.com/omarcordero1)")


# ─── Pantalla principal ───────────────────────────────────────────────────────
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption(APP_SUBTITLE)

if not archivo:
    st.info("👈 Sube un archivo Excel o CSV en el panel izquierdo para comenzar.")

    with st.expander("ℹ️ ¿Qué hace esta herramienta?", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🔍 Modelado de Temas")
            st.markdown("Usa **BERTopic** con embeddings multilingües para identificar clusters temáticos en tus titulares.")
        with col2:
            st.markdown("#### 👤 Extracción de Entidades")
            st.markdown("Aplica **spaCy NER** para identificar personajes, organizaciones y lugares en cada nota.")
        with col3:
            st.markdown("#### 📊 Clasificación de Impacto")
            st.markdown("Combina sección + tema + pageviews para generar segmentación editorial **accionable**.")
    st.stop()


# ─── Pipeline de análisis ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def ejecutar_pipeline(file_bytes: bytes, filename: str, min_topic: int) -> pd.DataFrame:
    """Pipeline cacheado para no re-ejecutar si los parámetros no cambian."""
    if filename.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))

    df = preparar_corpus(df)
    df, _ = asignar_temas(df, min_topic_size=min_topic)
    df = asignar_entidades(df)
    df = asignar_areas_impacto(df)
    return df


if ejecutar and archivo:
    with st.spinner("🔄 Procesando... esto puede tomar unos minutos (BERTopic + NER)"):
        try:
            file_bytes = archivo.read()
            df = ejecutar_pipeline(file_bytes, archivo.name, min_topic_size)
            st.session_state["df"] = df
            st.success(f"✅ Análisis completado — {len(df):,} noticias procesadas")
        except Exception as e:
            st.error(f"❌ Error durante el análisis: {str(e)}")
            st.stop()

# Mostrar resultados si están en sesión
if "df" not in st.session_state:
    st.stop()

df = st.session_state["df"]

# ─── KPIs ─────────────────────────────────────────────────────────────────────
st.markdown("### 📈 Métricas Generales")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📰 Total Noticias", f"{len(df):,}")
k2.metric("🏷️ Temas", df["tema"].nunique())
k3.metric("📂 Secciones", df["seccion"].nunique() if "seccion" in df.columns else "N/A")
k4.metric("👤 Entidades", (df["personaje_principal"] != "No identificado").sum())
k5.metric("📊 PV Promedio", f"{df['Pv´s'].mean():,.0f}" if "Pv´s" in df.columns else "N/A")

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_temas, tab_entidades, tab_impacto, tab_recomendaciones, tab_datos = st.tabs([
    "🔍 Temas", "👤 Entidades", "📊 Impacto", "💡 Recomendaciones", "📋 Datos"
])

# Tab 1: Temas
with tab_temas:
    st.markdown("#### Distribución de Temas Editoriales")
    col1, col2 = st.columns([3, 2])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        data = df["tema"].value_counts().head(top_n)
        data.sort_values().plot(kind="barh", ax=ax, color="#1a73e8", edgecolor="white")
        ax.set_title(f"Top {top_n} Temas Más Frecuentes", fontweight="bold")
        ax.set_xlabel("Cantidad de notas")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.markdown("##### PVs Promedio por Tema")
        tema_eng = df.groupby("tema")["Pv´s"].mean().sort_values(ascending=False).head(top_n)
        st.bar_chart(tema_eng)

# Tab 2: Entidades
with tab_entidades:
    st.markdown("#### Actores Principales en la Cobertura")
    col1, col2 = st.columns([3, 2])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        entidades = top_entidades(df, n=15)
        entidades.sort_values().plot(kind="barh", ax=ax, color="#34a853", edgecolor="white")
        ax.set_title("Top 15 Personajes/Organizaciones Más Mencionados", fontweight="bold")
        ax.set_xlabel("Apariciones")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.markdown("##### Ranking completo")
        st.dataframe(
            entidades.reset_index().rename(columns={"personaje_principal": "Entidad", "count": "Menciones"}),
            use_container_width=True
        )

# Tab 3: Impacto
with tab_impacto:
    st.markdown("#### Clasificación por Área de Impacto")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 5))
        data = df["area_impacto"].value_counts()
        colors = sns.color_palette("Set2", len(data))
        data.sort_values().plot(kind="barh", ax=ax, color=colors, edgecolor="white")
        ax.set_title("Distribución de Áreas de Impacto", fontweight="bold")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.markdown("##### Resumen estadístico")
        try:
            resumen = resumen_impacto(df)
            st.dataframe(resumen, use_container_width=True)
        except Exception:
            st.dataframe(df["area_impacto"].value_counts(), use_container_width=True)

# Tab 4: Recomendaciones
with tab_recomendaciones:
    st.markdown("#### 💡 Matriz de Recomendaciones para la Redacción")
    st.caption("Basada en frecuencia de cobertura, engagement promedio y entidades principales")

    try:
        recomendaciones = calcular_matriz_recomendaciones(df, top_n=15)
        st.dataframe(
            recomendaciones[["tema", "frecuencia", "engagement_promedio", "personaje_principal", "recomendacion"]],
            use_container_width=True,
            height=500
        )

        # Descargar CSV
        csv = recomendaciones.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 Descargar Recomendaciones (.csv)",
            data=csv,
            file_name="recomendaciones_editoriales.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.warning(f"No se pudo generar la matriz de recomendaciones: {e}")

# Tab 5: Datos
with tab_datos:
    st.markdown("#### 📋 Dataset Procesado")

    col_filter, col_section = st.columns(2)
    with col_filter:
        filtro_impacto = st.multiselect(
            "Filtrar por área de impacto",
            options=df["area_impacto"].unique().tolist(),
            default=[]
        )
    with col_section:
        filtro_seccion = st.multiselect(
            "Filtrar por sección",
            options=df["seccion"].unique().tolist() if "seccion" in df.columns else [],
            default=[]
        )

    df_filtrado = df.copy()
    if filtro_impacto:
        df_filtrado = df_filtrado[df_filtrado["area_impacto"].isin(filtro_impacto)]
    if filtro_seccion:
        df_filtrado = df_filtrado[df_filtrado["seccion"].isin(filtro_seccion)]

    columnas_mostrar = [c for c in ["titulo", "seccion", "tema", "personaje_principal", "area_impacto", "Pv´s", "editor"] if c in df.columns]
    st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True, height=400)
    st.caption(f"Mostrando {len(df_filtrado):,} registros")

    # Descargar análisis completo
    csv_completo = df_filtrado[columnas_mostrar].to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "📥 Descargar análisis completo (.csv)",
        data=csv_completo,
        file_name="milenio_analisis_completo.csv",
        mime="text/csv"
    )
