# Taller 2: Data Mastery (Premier League Analytics)
**Machine Learning I - Universidad Externado de Colombia**

Este repositorio ha sido simplificado y unificado para ofrecer una experiencia interactiva y fluida. Todo el análisis, desde la exploración inicial hasta el entrenamiento de modelos avanzados, se encuentra consolidado en dos Notebooks maestros.

---

## 🚀 Inicio Rápido

Para ejecutar el proyecto, solo necesitas descargar los datos y abrir los notebooks correspondientes.

### 1. Preparación

Clona el entorno y descarga los datos directamente de la API:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generales/download_data.py
```

### 2. Los Notebooks Maestros

*   **[📗 Modelo_1_Expected_Goals_V2.ipynb](./scripts/modelo_1_xg/Modelo_1_Expected_Goals_V2.ipynb)**: Tiros de la liga, análisis espacial y clasificador logístico de goles (xG). Incluye **Sección 9: Efectos de Jugador** — `β_jugador` estimado con regresión logística L2 sobre 70 jugadores con ≥30 tiros (7.198 disparos reales de Premier League 24/25).
*   **[📘 Modelo_2_Match_Predictor.ipynb](./scripts/modelo_2_partidos/Modelo_2_Match_Predictor.ipynb)**: El estudio de los partidos, la fatiga biológica y la regresión penalizada para predecir marcadores.

---

## 📂 Estructura del Repositorio

```text
.
├── audio/              # Clips de Mariano Closs para el dashboard interactivo
├── data/               # Datasets crudos (.csv) y matrices de oro
├── img/                # Gráficas generadas (ROC, Residuos, Confusión, Efectos Jugador)
├── guias_PDF/          # Documentación de apoyo y guías de clase
├── scripts/
│   ├── generales/      # Herramienta de descarga de datos
│   ├── modelo_1_xg/    # Notebook V2 + documentación técnica del Modelo 1
│   └── modelo_2_partidos/ # Notebook + documentación técnica del Modelo 2
├── dashboard.html      # Dashboard 3D interactivo con predictor xG en vivo
└── README.md           # Esta guía de inicio
```

---

## 📕 Documentación Detallada

*   [Detalles Modelo 1 (xG)](./scripts/modelo_1_xg/README_Modelo1_RegresionLogistica.md)
*   [Detalles Modelo 2 (Match Predictor)](./scripts/modelo_2_partidos/README_Modelo2_RegresionLineal.md)
