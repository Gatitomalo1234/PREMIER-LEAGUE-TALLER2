# Taller 2: Data Mastery (Premier League Analytics)
**Machine Learning I - Universidad Externado de Colombia**

Este repositorio ha sido simplificado y unificado para ofrecer una experiencia interactiva y fluida. Todo el an\u00e1lisis, desde la exploraci\u00f3n inicial hasta el entrenamiento de modelos avanzados, se encuentra consolidado en dos Notebooks maestros.

---

## 🚀 Inicio R\u00e1pido

Para ejecutar el proyecto, solo necesitas descargar los datos y abrir los notebooks correspondientes.

### 1. Preparaci\u00f3n
Clona el entorno y descarga los datos directamente de la API:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generales/download_data.py
```

### 2. Los Notebooks Maestros

*   **[📗 Modelo_1_Expected_Goals.ipynb](./scripts/modelo_1_xg/Modelo_1_Expected_Goals.ipynb)**: Todo sobre los tiros de la liga, el an\u00e1lisis espacial y el clasificador log\u00edstico de goles (xG).
*   **[📘 Modelo_2_Match_Predictor.ipynb](./scripts/modelo_2_partidos/Modelo_2_Match_Predictor.ipynb)**: El estudio de los partidos, la fatiga biol\u00f3gica y la regresi\u00f3n penalizada para predecir marcadores.

---

## 📂 Estructura del Repositorio Limpio

```text
TALLER 2/
├── guias_PDF/          # Documentaci\u00f3n de apoyo y gu\u00edas de clase
├── data/               # Datasets crudos (.csv) y matrices de oro
├── img/                # Gr\u00e1ficas generadas (ROC, Residuos, Confusi\u00f3n)
├── scripts/
│   ├── generales/      # Herramienta de descarga de datos
│   ├── modelo_1_xg/    # Documentaci\u00f3n t\u00e9cnica detallada del Modelo 1
│   └── modelo_2_partidos/ # Documentaci\u00f3n t\u00e9cnica detallada del Modelo 2
├── Modelo_1_Expected_Goals.ipynb
├── Modelo_2_Match_Predictor.ipynb
└── README.md           # Esta gu\u00eda de inicio
```

---

## 📕 Documentaci\u00f3n Detallada
Dentro de las carpetas de cada modelo en `scripts/`, encontrar\u00e1s los archivos `.md` originales con la desglose te\u00f3rico, los supuestos de Gauss-Markov y el an\u00e1lisis de betas para una consulta r\u00e1pida.

*   [Detalles Modelo 1 (xG)](./scripts/modelo_1_xg/README_Modelo1_RegresionLogistica.md)
*   [Detalles Modelo 2 (Match Predictor)](./scripts/modelo_2_partidos/README_Modelo2_RegresionLineal.md)
