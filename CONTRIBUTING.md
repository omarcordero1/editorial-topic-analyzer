# 🤝 Guía de Contribución

Gracias por tu interés en contribuir a **Milenio Cobertura Editorial**. Este documento describe el flujo de trabajo, convenciones y estándares del proyecto.

---

## 📋 Índice

1. [Primeros pasos](#primeros-pasos)
2. [Tipos de contribución](#tipos-de-contribución)
3. [Flujo de trabajo (Git)](#flujo-de-trabajo-git)
4. [Convenciones de código](#convenciones-de-código)
5. [Tests](#tests)
6. [Flujo de Pull Request](#flujo-de-pull-request)
7. [Reporte de bugs](#reporte-de-bugs)

---

## 🚀 Primeros Pasos

### 1. Fork y clona el repositorio

```bash
# Fork desde GitHub y luego:
git clone https://github.com/TU_USUARIO/milenio-cobertura-editorial.git
cd milenio-cobertura-editorial
```

### 2. Configura el entorno de desarrollo

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

pip install -r requirements.txt
python -m spacy download es_core_news_sm
cp .env.example .env
```

### 3. Verifica que todo funciona

```bash
pytest tests/ -v
```

---

## 🎯 Tipos de Contribución

| Tipo | Descripción |
|------|-------------|
| 🐛 **Bug fix** | Corrección de errores identificados |
| ✨ **Feature** | Nueva funcionalidad (siempre abrir issue primero) |
| 📖 **Docs** | Mejoras a README, docstrings o comentarios |
| ⚡ **Performance** | Optimizaciones de velocidad o memoria |
| 🧪 **Tests** | Nuevos tests o mejora de cobertura |
| 🎨 **Refactor** | Mejoras de código sin cambio de comportamiento |

---

## 🌿 Flujo de Trabajo (Git)

### Nombrado de ramas

```
feat/nombre-de-la-feature        # Nueva funcionalidad
fix/descripcion-del-bug          # Corrección de bug
docs/seccion-actualizada         # Documentación
test/modulo-cubierto             # Tests
refactor/nombre-del-modulo       # Refactoring
```

### Ejemplo completo

```bash
# 1. Sincroniza con main
git checkout main
git pull upstream main

# 2. Crea tu rama
git checkout -b feat/fastapi-endpoint

# 3. Trabaja y haz commits atómicos
git add src/api.py
git commit -m "feat(api): agregar endpoint /analyze para pipeline batch"

# 4. Push y abre PR
git push origin feat/fastapi-endpoint
```

---

## 🎨 Convenciones de Código

### Estilo general

Este proyecto sigue **PEP 8** con las siguientes herramientas configuradas:

```bash
# Formatear código
black src/ tests/ --line-length 100

# Ordenar imports
isort src/ tests/

# Verificar linting
flake8 src/ tests/ --max-line-length 100
```

### Convención de commits (Conventional Commits)

```
tipo(alcance): descripción corta en español

[cuerpo opcional — más detalle]

[footer opcional — closes #issue]
```

**Tipos válidos:**

| Tipo | Cuándo usarlo |
|------|--------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `test` | Agregar o modificar tests |
| `refactor` | Refactoring sin cambio funcional |
| `perf` | Mejora de rendimiento |
| `chore` | Tareas de mantenimiento (deps, CI) |

**Ejemplos correctos:**

```
feat(ner): agregar filtro de entidades genéricas por lista configurable
fix(bertopic): manejar excepción cuando corpus tiene menos de min_topic_size textos
docs(readme): agregar sección de formato del dataset con tabla de columnas
test(impact): cubrir caso de pv nulo con pytest parametrize
```

### Docstrings

Todos los módulos, clases y funciones públicas deben tener docstrings en formato Google:

```python
def clasificar_impacto(row: pd.Series, thresholds: ThresholdsConfig) -> str:
    """
    Clasifica una noticia en su área de impacto editorial.

    Args:
        row: Fila del DataFrame con campos 'tema', 'seccion', 'Pv´s'
        thresholds: Umbrales de PVs configurables

    Returns:
        Etiqueta de área de impacto como string

    Raises:
        KeyError: Si 'Pv´s' no existe en la fila y no hay fallback
    """
```

### Type hints

Todas las funciones públicas deben tener type hints completos:

```python
# ✅ Correcto
def cargar_dataset(ruta: str, max_columnas: int = 16) -> pd.DataFrame:
    ...

# ❌ Incorrecto
def cargar_dataset(ruta, max_columnas=16):
    ...
```

### Logging vs print

Siempre usar `logging`, nunca `print()` en módulos de `src/`:

```python
# ✅ Correcto
import logging
logger = logging.getLogger(__name__)
logger.info("Corpus preparado: 1,000 textos")

# ❌ Incorrecto
print("Corpus preparado: 1,000 textos")
```

---

## 🧪 Tests

### Ejecutar tests

```bash
# Todos los tests
pytest tests/ -v

# Con reporte de cobertura
pytest tests/ --cov=src --cov-report=term-missing

# Un módulo específico
pytest tests/test_text_cleaner.py -v
```

### Convenciones para tests

- Un archivo de test por módulo: `test_nombre_modulo.py`
- Clases de test agrupan casos relacionados: `class TestLimpiarTexto`
- Nombres descriptivos: `test_elimina_acentos_de_texto_normal`
- Fixtures para datos compartidos entre tests
- Cada test valida una sola cosa

```python
# ✅ Correcto — test atómico y descriptivo
def test_limpiar_texto_elimina_url():
    resultado = limpiar_texto("Ver más en https://milenio.com/nota")
    assert "http" not in resultado

# ❌ Incorrecto — test que verifica múltiples cosas
def test_limpiar_texto():
    assert limpiar_texto("AMLO") == "amlo"
    assert limpiar_texto(None) == ""
    assert "http" not in limpiar_texto("https://x.com")
```

### Cobertura mínima requerida

Se requiere **70% de cobertura** en módulos de `src/` para que el PR sea aceptado.

---

## 📬 Flujo de Pull Request

### Antes de abrir el PR

```bash
# 1. Tests pasan
pytest tests/ -v

# 2. Código formateado
black src/ tests/ --check

# 3. Sin errores de linting
flake8 src/ tests/ --max-line-length 100

# 4. Sin conflictos con main
git rebase main
```

### Checklist del PR

Al abrir el Pull Request, asegúrate de marcar:

- [ ] Tests agregados o actualizados para el cambio
- [ ] Docstrings actualizados
- [ ] README actualizado si es necesario
- [ ] `.env.example` actualizado si se agregan nuevas variables
- [ ] No se incluyen archivos de datos ni credenciales

### Proceso de revisión

1. Abre el PR con descripción clara de qué y por qué
2. Asigna el label apropiado (`bug`, `enhancement`, `documentation`)
3. El maintainer revisará en máximo 5 días hábiles
4. Aplica los cambios solicitados con commits adicionales (no force-push durante review)
5. Una vez aprobado, se hace squash merge a main

---

## 🐛 Reporte de Bugs

Usa el template de issues de GitHub e incluye:

1. **Descripción**: Qué esperabas vs qué ocurrió
2. **Pasos para reproducir**: Comandos exactos que ejecutaste
3. **Entorno**: OS, versión de Python, versiones de dependencias (`pip freeze`)
4. **Dataset**: Descripción del formato de datos (sin datos reales)
5. **Logs**: Copia el traceback completo

```bash
# Generar info de entorno para el bug report
python --version
pip freeze | grep -E "bertopic|spacy|pandas|streamlit"
```

---

## 💬 ¿Preguntas?

Abre un [issue de discusión](https://github.com/omarcordero1/milenio-cobertura-editorial/issues/new?labels=question) o contacta directamente en [LinkedIn](https://www.linkedin.com/in/omar-said-cordero-lugo).

---

<div align="center">
  <sub>¡Gracias por hacer este proyecto mejor para las redacciones! 🗞️</sub>
</div>
