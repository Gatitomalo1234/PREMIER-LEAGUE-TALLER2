# VORTEX | Premier League Neural Intelligence

Proyecto final de Machine Learning - Análisis Predictivo de la Premier League mediante Expected Goals (xG) y Modelos Multinomiales.

---

## 👥 Integrantes

*   **Nicolas Cardenas Diaz**
*   **Maria Paula Muñoz Malaver**

---

## 🌐 Dashboard en Vivo

Puedes acceder al panel interactivo 3D y simulador de xG aquí:

👉 **[Link del Dashboard en Netlify](URL_AQUÍ)**

---

## 🚀 Descripción del Proyecto
Este proyecto implementa un ecosistema predictivo para fútbol profesional dividido en dos núcleos principales:

### 1. Modelo de Expected Goals (xG) - Logístico Binario
*   **Enfoque**: Clasificación logística calibrada mediante Platt Scaling.
*   **Features**: Distancia al arco, ángulo de tiro, indicador de Big Chance, situación de penalti y mano a mano.
*   **Resultados**: AUC-ROC de 0.836 y calibración estadística mediante Reliability Diagrams.

### 2. Predictor de Resultados de Partido - Logístico Multinomial (H/D/A)
*   **Enfoque**: Regresión multinomial para predecir Local, Empate o Visitante.
*   **Features**: Diferencial de xG acumulado, fatiga biológica de los jugadores y cuotas de mercado como baseline.
*   **Resultados**: Capacidad predictiva que supera el baseline de mercado (Bet365) en un 1.69%.

---

## 📂 Estructura del Repositorio
```text
.
├── audio/              # Narraciones interactivas (Mariano Closs & Bambino Pons)
├── data/               # Datasets crudos y procesados
├── img/                # Gráficas de validación (ROC, Confusión, Curvas de Calibración)
├── scripts/
│   ├── modelo_1_xg/    # Notebooks de EDA + Entrenamiento del Modelo xG
│   └── modelo_2_partidos/ # Notebooks de Predicción de Resultados (Match Predictor)
├── dashboard.html      # Aplicación web interactiva (Front-end 3D)
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación principal
```

---

## ⚙️ Instrucciones de Ejecución

### Requisitos Previos
Asegúrate de tener Python 3.9+ instalado. Se recomienda usar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Ejecución de Notebooks
1. Navega a `scripts/modelo_1_xg/` para el análisis de xG.
2. Navega a `scripts/modelo_2_partidos/` para el predictor de partidos.
3. Abre los archivos `.ipynb` mediante Jupyter Lab o VS Code.

### Visualización del Dashboard
Simplemente abre el archivo `dashboard.html` en cualquier navegador moderno. Para una experiencia completa, asegúrate de tener conexión a internet para cargar las fuentes y texturas 3D.

---

## 🛠️ Tecnologías Utilizadas
*   **Análisis de Datos**: Pandas, NumPy, Statsmodels.
*   **Visualización Científica**: Matplotlib, Seaborn, Mplsoccer.
*   **Machine Learning**: Scikit-Learn (LogisticRegression, CalibratedClassifierCV).
*   **Front-end**: HTML5, CSS3 (Glassmorphism), Three.js (WebGL), Vanilla JS.
