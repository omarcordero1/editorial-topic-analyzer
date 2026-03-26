# 📰 Milenio Cobertura Editorial — Análisis Inteligente de Noticias

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BERTopic](https://img.shields.io/badge/BERTopic-NLP-FF6F00?style=for-the-badge)
![spaCy](https://img.shields.io/badge/spaCy-NER-09A3D5?style=for-the-badge&logo=spaCy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Pipeline de análisis editorial que extrae temas, entidades y variables accionables a partir de coberturas periodísticas de Milenio.com.**

[🚀 Demo Live](#) · [📖 Documentación](#uso) · [🐛 Reportar Bug](https://github.com/omarcordero1/milenio-cobertura-editorial/issues)

</div>

---

## 🎯 El Problema que Resuelve

Las redacciones periodísticas generan cientos de notas diarias, pero **toman decisiones editoriales sin datos**. ¿Qué temas generan más engagement? ¿Qué actores capturan la atención del lector? ¿Dónde debe enfocar su energía un editor?

Este proyecto convierte un dataset de titulares y métricas de pageviews en **inteligencia editorial accionable**, automatizando análisis que tomarían días en horas.

---

## 💡 ¿Qué hace?

| Módulo | Tecnología | Output |
|--------|-----------|--------|
| 🔍 **Modelado de Temas** | BERTopic + Embeddings multilingües | Clusters semánticos de cobertura |
| 👤 **Extracción de Entidades** | spaCy NER (es_core_news_sm) | Personajes, organizaciones, lugares |
| 📊 **Clasificación de Impacto** | Reglas + Métricas de engagement | Segmentación editorial accionable |
| 💡 **Recomendaciones** | Análisis estadístico | Matriz de prioridades para la redacción |
| 📈 **Dashboard** | Streamlit + Matplotlib | Visualizaciones interactivas |

---

## 🗂️ Estructura del Proyecto

```
milenio-cobertura-editorial/
│
├── 📁 src/                          # Módulos principales
│   ├── data_loader.py               # Carga y validación de datasets
│   ├── text_cleaner.py              # Limpieza y normalización NLP
│   ├── topic_modeling.py            # BERTopic — modelado de temas
│   ├── ner_extractor.py             # spaCy — extracción de entidades
│   ├── impact_classifier.py         # Clasificador de áreas de impacto
│   ├── recommender.py               # Generador de recomendaciones
│   └── visualizer.py                # Visualizaciones matplotlib
│
├── 📁 app/
│   └── app.py                       # Dashboard Streamlit interactivo
│
├── 📁 notebooks/
│   └── Segmentacion_original.ipynb  # Notebook original (Colab)
│
├── 📁 config/
│   └── settings.py                  # Configuración centralizada
│
├── 📁 tests/
│   ├── test_text_cleaner.py
│   └── test_impact_classifier.py
│
├── 📁 data/                         # Datasets (no versionados)
│   └── .gitkeep
│
├── 📁 outputs/                      # Resultados generados
│   └── .gitkeep
│
├── main.py                          # Pipeline CLI principal
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/omarcordero1/milenio-cobertura-editorial.git
cd milenio-cobertura-editorial
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones si necesitas ajustar umbrales
```

---

## 🚀 Uso

### Opción A — Pipeline CLI (batch)

Ejecuta el análisis completo sobre un archivo Excel o CSV:

```bash
python main.py --input data/Base_de_trabajo.xlsx
```

Con parámetros personalizados:

```bash
python main.py \
  --input data/noticias.csv \
  --output outputs/reporte_enero \
  --min-topic-size 20 \
  --no-viz
```

**Argumentos disponibles:**

| Argumento | Descripción | Default |
|-----------|-------------|---------|
| `--input` | Ruta al archivo `.xlsx` o `.csv` | requerido |
| `--output` | Directorio de salida | `outputs/` |
| `--min-topic-size` | Mínimo de artículos por cluster | `30` |
| `--no-viz` | Omite la generación del dashboard | `False` |

### Opción B — Dashboard Streamlit (interactivo)

```bash
streamlit run app/app.py
```

Abre `http://localhost:8501` en tu navegador y sube el archivo directamente.

### Opción C — Como módulo Python

```python
from src.data_loader import cargar_dataset
from src.text_cleaner import preparar_corpus
from src.topic_modeling import asignar_temas
from src.ner_extractor import asignar_entidades
from src.impact_classifier import asignar_areas_impacto
from src.recommender import calcular_matriz_recomendaciones

# Pipeline mínimo
df = cargar_dataset("data/Base_de_trabajo.xlsx")
df = preparar_corpus(df)
df, modelo = asignar_temas(df)
df = asignar_entidades(df)
df = asignar_areas_impacto(df)

recomendaciones = calcular_matriz_recomendaciones(df)
print(recomendaciones)
```

---

## 📋 Formato del Dataset

El sistema espera un archivo Excel o CSV con al menos estas columnas:

| Columna | Tipo | Descripción | Requerida |
|---------|------|-------------|-----------|
| `titulo` | string | Titular de la nota | ✅ |
| `seccion` | string | Sección editorial (Política, Deportes...) | ✅ |
| `Pv´s` | número | Pageviews de la nota | ✅ |
| `id` | string/int | Identificador único | Opcional |
| `URL` | string | URL de la nota | Opcional |
| `editor` | string | Nombre del editor | Opcional |
| `plaza` | string | Ciudad/plaza | Opcional |
| `Fecha` | date | Fecha de publicación | Opcional |

---

## 📊 Outputs Generados

Después de ejecutar el pipeline, encontrarás en `outputs/`:

```
outputs/
├── Milenio_Analisis_Completo.csv       # Dataset original + variables enriquecidas
├── Milenio_Recomendaciones.csv         # Matriz de recomendaciones por tema
├── analisis_editorial.png              # Dashboard visual 2×2
└── pipeline.log                        # Log de ejecución
```

### Variables añadidas al dataset

| Variable | Descripción |
|----------|-------------|
| `tema` | Cluster semántico (ej: `"gobierno + presupuesto + decreto"`) |
| `tema_id` | ID numérico del cluster BERTopic |
| `tema_probabilidad` | Confianza de asignación al cluster (0–1) |
| `personaje_principal` | Entidad más relevante del titular |
| `area_impacto` | Segmento editorial accionable |

### Áreas de impacto disponibles

```
CRÍTICO - Alto Impacto        → Política/Economía + PVs altos
CRÍTICO - Bajo Impacto        → Política/Economía + PVs bajos (¡ojo! subutilizado)
ENTRETENIMIENTO - Viral       → Deportes + PVs altos
ENTRETENIMIENTO - Nicho       → Deportes + PVs bajos
NEGOCIOS - B2B Focus          → Temas de mercado/empresa
SOCIAL - Tendencia            → Comunidad + PVs altos
SOCIAL - Comunidad Local      → Comunidad + PVs bajos
GENERAL - Destacable          → Sin categoría + PVs razonables
GENERAL - Regularidad         → Sin categoría + bajo engagement
```

---

## 🖥️ Screenshots

> **Dashboard principal** — Vista general 2×2 con temas, impacto, entidades y engagement por tema

```
┌─────────────────────┬──────────────────────┐
│  Top 8 Temas        │  Áreas de Impacto    │
│  (barras horiz.)    │  (distribución)      │
├─────────────────────┼──────────────────────┤
│  Top Actores        │  PVs por Tema        │
│  Principales        │  (barras vertical)   │
└─────────────────────┴──────────────────────┘
```

> **App Streamlit** — Subida de archivo → análisis automático → filtros por sección/impacto → descarga CSV

---

## 🧠 Arquitectura y Decisiones Técnicas

### ¿Por qué BERTopic?

BERTopic usa embeddings de transformers multilingües para capturar semántica profunda, superando enfoques bag-of-words (LDA/NMF) para corpus periodísticos en español donde el contexto importa.

### ¿Por qué spaCy sobre BERT-NER?

`es_core_news_sm` de spaCy ofrece un equilibrio excelente entre velocidad y precisión para NER en español. Para producción con volumen alto, se puede upgradar a `es_core_news_lg` o fine-tuning con datos propios de Milenio.

### Clasificación de impacto

Usa reglas interpretables (no caja negra) porque las redacciones necesitan explicar sus decisiones. Los umbrales son configurables via `.env` para adaptarse a diferentes medios o periodos.

---

## 🗺️ Roadmap

- [x] Pipeline base (BERTopic + NER + Clasificación)
- [x] Dashboard Streamlit
- [x] Tests unitarios
- [ ] Fine-tuning de NER con corpus Milenio
- [ ] API REST con FastAPI
- [ ] Procesamiento en streaming (artículos en tiempo real)
- [ ] Integración con Google Search Console
- [ ] Soporte multi-marca (Mediotiempo, Telediario, Chic)
- [ ] Alertas automáticas vía Slack/Email
- [ ] Clustering temporal (tendencias semana a semana)

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para el flujo de trabajo.

---

## 👤 Autor

**Omar Said Cordero Lugo**
Data Scientist · Grupo Multimedios

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Omar_Cordero-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/omar-said-cordero-lugo)
[![GitHub](https://img.shields.io/badge/GitHub-omarcordero1-181717?style=flat&logo=github)](https://github.com/omarcordero1)

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

---

<div align="center">
  <sub>Construido con ❤️ para periodistas que creen en los datos</sub>
</div>
