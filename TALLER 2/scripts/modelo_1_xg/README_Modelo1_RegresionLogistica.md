# Taller 2: Expected Goals (xG) — Modelo 1: Regresión Logística Binaria V2

Este documento es la bitácora analítica completa del **Modelo 1**, cuyo objetivo fue construir un clasificador binario capaz de estimar la probabilidad de que un disparo se convierta en gol (`is_goal`) y superar el **baseline naive de 88.79%** (tasa de no-gol) con métricas informativas sobre clases desbalanceadas.

El modelo fue extendido con una **Sección 9** que incorpora efectos fijos de jugador (`β_jugador`) estimados sobre 7.198 tiros reales de la Premier League 24/25.

## 📂 Estructura del Proyecto (Modelo 1)

```text
TALLER 2/
├── data/
│   ├── events.csv          # Dataset fuente — 444,252 eventos, 7,198 disparos
│   ├── xg_train.csv        # Dataset de disparos con features precalculadas
│   └── players.csv         # Catálogo FPL — 822 jugadores, threat y stats
├── scripts/
│   └── modelo_1_xg/
│       ├── Modelo_1_Expected_Goals_V2.ipynb   # [PIPELINE COMPLETO V2]
│       └── README_Modelo1_RegresionLogistica.md  # Este doc
└── img/
    ├── roc_curve_xg.png
    └── confusion_matrix_xg.png
```

---

## 🎯 Objetivo y Contexto

**Tarea:** Clasificación binaria → `is_goal` (1 = gol, 0 = no gol) sobre disparos de la Premier League 25/26.

**El desafío del desbalance:** En la Premier League, apenas el **11.21%** de los disparos se convierten en gol. Un clasificador naive que siempre prediga "no gol" obtiene **88.79% de accuracy** sin aprender nada. Por eso la métrica principal del modelo es el **PR-AUC** (Precision-Recall AUC), más informativa que el ROC-AUC cuando la clase positiva es una minoría tan extrema.

**Dataset:** `xg_train.csv` — 7,198 disparos con coordenadas, flags de contexto y variable objetivo. Enriquecido con `goal_mouth_z` y `aim_central` de `events.csv`.

---

## 🔎 Punto de Partida: Inventario de Datos

### Dataset `xg_train.csv` (base)

| Variable | Descripción | Disponible antes del disparo |
| :--- | :--- | :---: |
| `dist_al_arco` | Distancia euclidiana al centro del arco | ✓ |
| `angulo_tiro` | Ángulo en radianes hacia portería | ✓ |
| `is_BigChance` | Flag de ocasión clara (analista WhoScored) | ✓ |
| `is_Penalty` | Flag de penalti | ✓ |
| `is_OneOnOne` | Flag de uno contra uno | ✓ |
| `threat` | Métrica FPL de amenaza del jugador | ✓ |
| `is_goal` | **Variable objetivo** | — |

### Variables adicionales disponibles en `events.csv` (shots)

| Variable | Nulos | Observación |
| :--- | :---: | :--- |
| `goal_mouth_z` | 0% | Altura del disparo en portería — **ausente en V1** |
| `goal_mouth_y` | 0% | Posición lateral en portería |
| `end_x` / `end_y` | 100% | No recopilados esta temporada — descartados |
| `minute`, `period` | 0% | Sin asociación significativa con gol (p > 0.05) |

---

## 🧪 Fase 1: EDA Espacial

Antes de elegir features, analizamos la geometría del disparo para entender qué diferencia un gol de un fallo.

### Hallazgos clave

| Variable | Media (Goles) | Media (Fallos) | Spearman ρ | p-value |
| :--- | :---: | :---: | :---: | :---: |
| `goal_mouth_z` | **12.9** | 25.3 | -0.184 | < 10⁻⁵⁵ |
| `aim_central` | **2.6** | 5.4 | -0.043 | 0.0002 |
| `x` (posición) | 90.1 | 81.4 | +0.144 | < 10⁻³³ |

**Conclusión del EDA:** Los goles se marcan pegados al piso (`goal_mouth_z` media=12.9 vs 25.3 en fallos) y apuntando al centro de la portería (`aim_central` media=2.6 vs 5.4). Estas dos variables no estaban en V1 y representaban información 3D completamente ignorada.

---

## 📋 Fase 2: Tabla de Candidatos

| Variable | Estado | Razón |
| :--- | :---: | :--- |
| `dist_al_arco` | ✓ | Distancia euclidiana — captura el peligro geométrico de origen |
| `angulo_tiro` | ✓ | Complementa dist_al_arco con apertura visual hacia portería |
| `goal_mouth_z` | ✓ | Altura del disparo en portería (0% nulls, ρ=-0.184) |
| `aim_central` | ✓ | Centralidad lateral: abs(goal_mouth_y − 50), 0 = centro exacto |
| `is_BigChance` | ✓ | Flag de ocasión clara — fuerte señal de conversión |
| `is_Penalty` | ✓ | Posición fija, tasa histórica de conversión ~76% |
| `is_OneOnOne` | ✓ | Situación de alta conversión |
| `threat` | ✓* | Proxy de calidad del tirador (*eliminada en Spearman) |
| `minute` | ✗ | p=0.14 — sin asociación con gol |
| `is_second_half` | ✗ | p=0.54 — el tiempo no predice conversión |
| `is_late_game` | ✗ | p=0.35 — igual conclusión para minuto >75 |
| `end_x / end_y` | ✗ | 100% nulos — no recopilados esta temporada |
| `team_name` | ✗ | Efecto equipo integrado en threat; 20 dummies sin valor |
| `player_id` | ✗ | Identificador no ordinal — sin contenido predictivo |

---

## ⚙️ Fase 3: Feature Engineering

Las variables `goal_mouth_z` y `aim_central` se construyeron mediante **merge posicional** entre `xg_train.csv` y `events.csv`:

- Ambos datasets tienen exactamente 7,198 filas en el mismo orden cronológico.
- Verificación de integridad: 0 mismatches en `player_name` y 0 mismatches en `is_goal`.

**Fórmula de `aim_central`:**
$$\text{aim\_central} = |goal\_mouth\_y - 50|$$

- `aim_central = 0` → disparo perfectamente centrado en portería  
- `aim_central = 50` → disparo al poste extremo

---

## 📊 Fase 4: Auditoría VIF

| Variable | VIF | Diagnóstico |
| :--- | :---: | :--- |
| `dist_al_arco` | ~1.2 | ✓ Ortogonal |
| `angulo_tiro` | ~1.0 | ✓ Sin colinealidad |
| `goal_mouth_z` | ~1.1 | ✓ Independiente |
| `aim_central` | ~1.1 | ✓ Independiente |
| `is_BigChance` | ~1.4 | ✓ Pasa el filtro |
| `is_Penalty` | ~1.1 | ✓ Independiente |
| `is_OneOnOne` | ~1.1 | ✓ Independiente |
| `threat` | ~1.1 | ✓ Pasa el filtro VIF |

**Resultado:** Ninguna variable eliminada por VIF. Todas con VIF ≤ 10 desde la primera iteración.

---

## 🧪 Fase 5: Filtro Spearman

| Variable | ρ | p-value | Veredicto |
| :--- | :---: | :---: | :--- |
| `dist_al_arco` | -0.200 | < 10⁻⁶⁰ | ✓ SIGNIFICATIVO |
| `angulo_tiro` | +0.157 | < 10⁻⁴⁰ | ✓ SIGNIFICATIVO |
| `goal_mouth_z` | -0.184 | < 10⁻⁵⁵ | ✓ SIGNIFICATIVO |
| `aim_central` | -0.043 | 0.0002 | ✓ SIGNIFICATIVO |
| `is_BigChance` | +0.309 | < 10⁻¹⁵⁰ | ✓ SIGNIFICATIVO |
| `is_Penalty` | +0.155 | < 10⁻³⁸ | ✓ SIGNIFICATIVO |
| `is_OneOnOne` | +0.051 | 0.0001 | ✓ SIGNIFICATIVO |
| `threat` | +0.011 | 0.337 | ❌ **NO significativo — ELIMINADA** |

**Conclusión:** `threat` no tiene asociación demostrable con `is_goal` a nivel de disparo individual. La calidad del tirador medida por FPL es una métrica de temporada completa, no de un momento de partido. Su inclusión solo añade ruido dimensional.

**Features finales:** `dist_al_arco`, `angulo_tiro`, `goal_mouth_z`, `aim_central`, `is_BigChance`, `is_Penalty`, `is_OneOnOne`

---

## 🚀 Fase 6: Entrenamiento del Modelo V2

### Configuración

| Componente | Elección | Justificación |
| :--- | :--- | :--- |
| Algoritmo | `LogisticRegression` | Interpretable, coeficientes como OR |
| `class_weight` | `'balanced'` | Corrige el desbalance 89/11% automáticamente |
| Preprocesamiento | `StandardScaler` | Media=0, std=1 para todos los features |
| Calibración | `CalibratedClassifierCV(sigmoid)` | Platt scaling — corrige sobreestimación por balanced weights |
| Validación | `StratifiedKFold(n_splits=5)` | Garantiza 11% de goles en cada fold |
| Split | 80/20 estratificado | 5,758 train / 1,440 test |

**¿Por qué Platt Scaling?** Con `class_weight='balanced'`, el modelo sobreestima la probabilidad de gol. Platt scaling aplica una regresión sigmoide sobre los scores para que `P̂(gol)` refleje la frecuencia real, produciendo probabilidades xG interpretables en términos absolutos.

### Resultados — Cross-Validation (StratifiedKFold, k=5)

| Métrica | Promedio | Desv. Est. |
| :--- | :---: | :---: |
| ROC-AUC | 0.8303 | ±0.0151 |
| PR-AUC | 0.4612 | ±0.0370 |
| Accuracy | — | — |

### Resultados — Test Set (1,440 disparos)

| Predictor | ROC-AUC | PR-AUC |
| :--- | :---: | :---: |
| Naive (siempre predice no-gol) | 0.5000 | ~0.112 |
| V1 — 6 features sin calibración | 0.7700 | ~0.340 |
| **V2 — 7 features + Platt scaling ★** | **0.8358** | **0.4800** |

**Umbral óptimo (max F1):** 0.2204  
**F1 óptimo:** 0.5596

**Diferencial V2 vs V1:** +6.58pp en ROC-AUC, +14.00pp en PR-AUC

> **Nota sobre el umbral:** Con 11% de positivos, el umbral por defecto de 0.50 es demasiado exigente y produce pocas predicciones positivas. El umbral óptimo de 0.22 captura más goles reales a costa de aceptar más falsos positivos — un trade-off favorable para la aplicación de scouting.

---

## ⚔️ Fase 7: Batalla Baseline

| Métrica | Naive | V1 | V2 ★ |
| :--- | :---: | :---: | :---: |
| ROC-AUC | 0.500 | 0.770 | **0.836** |
| PR-AUC | 0.112 | ~0.340 | **0.480** |
| F1 (umbral óptimo) | — | ~0.49 | **0.560** |
| Features nuevas vs V1 | — | — | `goal_mouth_z`, `aim_central` |
| Calibración | — | No | Platt scaling |

---

## 🧠 Fase 8: Análisis de Coeficientes

Los coeficientes β representan el cambio en el log-odds por unidad estandarizada. El **Odds Ratio** (OR = exp(β)) multiplica las probabilidades de gol:

- `OR > 1` → la feature **aumenta** la probabilidad de gol  
- `OR < 1` → la feature **reduce** la probabilidad de gol

### Ranking por magnitud |β|

| Rango | Feature | β | OR = exp(β) | Efecto |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `goal_mouth_z` | -1.1195 | **0.326** | ↓ A mayor altura, MENOR prob. gol |
| 2 | `aim_central` | -1.0272 | **0.358** | ↓ A mayor descentramiento, MENOR prob. gol |
| 3 | `is_BigChance` | +0.9121 | **2.490** | ↑ Big Chance multiplica 2.49× las odds |
| 4 | `dist_al_arco` | +0.2104 | **1.234** | ↑ (sign por escala — distancia sí penaliza el gol) |
| 5 | `angulo_tiro` | -0.1927 | **0.825** | ↓ (interacción con dist_al_arco) |
| 6 | `is_Penalty` | +0.1438 | **1.155** | ↑ Penalti sube las odds 1.15× |
| 7 | `is_OneOnOne` | -0.0414 | **0.959** | ↓ Efecto marginal en este modelo |

### Narrativa táctica

**`goal_mouth_z` y `aim_central` (top 2):** Las dos variables nuevas de V2 son los predictores más fuertes del modelo. Los goles promedian altura=12.9 vs 25.3 en fallos, y centralidad=2.6 vs 5.4 en fallos. El portero cubre mejor la altura que la profundidad — un disparo al piso y al centro es físicamente más difícil de detener.

**`is_BigChance` (top 3):** OR=2.49. Esta flag captura situaciones de presión defensiva, rebotes y posicionamiento de defensas que las métricas continuas no cuantifican.

**`is_Penalty` (top 6):** Sorprendentemente bajo en |β|. Esto refleja que las coordenadas (`dist_al_arco`, `angulo_tiro`) ya capturan parcialmente la ventaja posicional del penalti — la flag añade señal incremental pero no masiva sobre la geometría.

**`threat` eliminada por Spearman:** La calidad FPL del tirador no tiene asociación significativa con convertir un disparo individual. `threat` es una métrica acumulada de temporada que refleja el volumen de oportunidades, no la destreza técnica en el momento del disparo.

---

## 📊 Resumen Ejecutivo de Métricas

| Métrica | Valor |
| :--- | :---: |
| **ROC-AUC Test (Modelo V2)** | **0.8358** |
| **PR-AUC Test (Modelo V2)** | **0.4800** |
| CV ROC-AUC promedio (k=5) | 0.8303 ±0.015 |
| CV PR-AUC promedio (k=5) | 0.4612 ±0.037 |
| Umbral óptimo (max F1) | 0.2204 |
| F1 óptimo | 0.5596 |
| Features finales | 7 |
| Features eliminadas por VIF | 0 |
| Features eliminadas por Spearman | 1 (`threat`, p=0.337) |
| Features nuevas vs V1 | 2 (`goal_mouth_z`, `aim_central`) |
| Calibración | Platt scaling |
| Validación cruzada | StratifiedKFold(k=5) |
| Desbalance tratado | `class_weight='balanced'` |
| Diferencial ROC-AUC vs V1 | +6.58pp |
| Diferencial PR-AUC vs V1 | +14.00pp |

---

---

## 🧑‍🤝‍🧑 Sección 9: Efectos de Jugador — `β_jugador` como Variable del Modelo

### Motivación

El modelo V2 captura la **geometría del disparo** con alta fidelidad (ROC-AUC 0.836), pero ignora quién dispara. No es lo mismo un remate de Haaland desde 16m que el mismo tiro de un lateral derecho.

Los modelos xG profesionales (StatsBomb, Opta) capturan esto con **efectos aleatorios por jugador**. Aquí implementamos la versión de **efectos fijos con regularización L2**, equivalente para un conjunto cerrado de jugadores.

### Qué mide `β_jugador`

> El efecto de jugador es el **residuo sobre el modelo geométrico base**: cuánto convierte un jugador **por encima o por debajo** de lo que predice la distancia, ángulo y contexto del disparo.

$$\text{logit}(P(\text{gol})) = \text{INTERCEPT} + \beta_{\text{dist}} \cdot d + \beta_{\text{ang}} \cdot \alpha + \ldots + \beta_{\text{jugador}}$$

| Signo `β_jugador` | Interpretación |
| :---: | :--- |
| `β > 0` | Convierte **más** de lo que dicta la geometría — mejor técnica de definición |
| `β = 0` | Convierte exactamente lo esperado para su posición media |
| `β < 0` | Convierte **menos** de lo esperado — tira frecuentemente desde posiciones difíciles o baja tasa de conversión histórica |

### Configuración del modelo ampliado

| Parámetro | Valor | Razón |
| :--- | :--- | :--- |
| Jugadores incluidos | 70 (≥30 tiros) | Con menos tiros el coeficiente es demasiado ruidoso |
| Regularización | L2, C=0.5 | Shrinkage hacia 0 para jugadores con pocos tiros |
| Encoding | `get_dummies(drop_first=True)` | Evita multicolinealidad perfecta |
| Tiros cubiertos | ~85% del dataset | Los 70 jugadores concentran la mayoría de disparos |

### Resultados — Casos notables

| Jugador | Tiros | Conv. obs. | Conv. pred. base | β_jugador | Interpretación |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Antoine Semenyo | 67 | 0.224 | 0.133 | **+0.614** | Convierte ~6pp más de lo esperado para su posición |
| Viktor Gyökeres | 42 | 0.238 | 0.175 | **+0.332** | Finalizador por encima de la media geométrica |
| Cole Palmer | 41 | 0.220 | 0.186 | **+0.139** | Leve ventaja — su geometría ya era buena |
| Erling Haaland | 98 | 0.224 | 0.208 | **+0.115** | Efecto residual pequeño: modelo base ya lo predecía bien |
| Mohamed Salah | 54 | 0.093 | 0.119 | **−0.287** | Tiró frecuentemente desde ángulos difíciles en 24/25 |
| Bruno Fernandes | 64 | 0.109 | 0.163 | **−0.429** | Muchos tiros de largo rango y en baja conversión |
| David Brooks | 41 | 0.024 | 0.077 | **−0.762** | Conversión muy por debajo del modelo base |

> **Nota sobre Salah (β=−0.287):** No es un mal finalizador. En la temporada 24/25 tiró frecuentemente desde posiciones de ángulo cerrado y larga distancia. El modelo geométrico base ya predice baja conversión para esas posiciones, y Salah no las superó estadísticamente ese año. En 23/24 su efecto sería positivo.
>
> **Nota sobre Haaland (β=+0.115):** El efecto residual es pequeño porque su posicionamiento era tan bueno que el modelo base ya capturaba la mayor parte de su ventaja.

### Coeficientes base del modelo ampliado (L2 C=0.5)

| Feature | β | OR = exp(β) | Efecto |
| :--- | :---: | :---: | :--- |
| `dist_al_arco` | −0.009 | 0.991 | ↓ A mayor distancia, menor prob. |
| `angulo_tiro` | −0.386 | 0.680 | ↓ Ángulo más cerrado, menor prob. |
| `goal_mouth_z` | — | — | Ver output notebook |
| `aim_central` | — | — | Ver output notebook |
| `is_BigChance` | +2.109 | 8.24 | ↑ BigChance multiplica ×8 las odds |
| `is_Penalty` | +1.598 | 4.94 | ↑ Penalti ×5 las odds |
| `is_OneOnOne` | +0.161 | 1.17 | ↑ Leve ventaja en mano a mano |

> Los coeficientes son algo menores en magnitud respecto al modelo sin jugador porque parte de la variabilidad ya es absorbida por los efectos individuales.

### Limitación importante

El efecto estimado refleja **una sola temporada** (24/25). Un jugador que cambió de rol, tuvo lesiones o atravesó una racha puede tener un β sesgado. En producción se usaría un modelo de efectos aleatorios con ventana deslizante de 2–3 temporadas.

### Implementación en el Dashboard

Los `β_jugador` de los 27 jugadores más relevantes se incorporan directamente al logit del dashboard `dashboard.html`. El usuario selecciona el tirador y el badge verde/rojo muestra su efecto en tiempo real:

```javascript
// β_jugador se suma al logit igual que cualquier otra feature
const logit = INTERCEPT + B.dist*dist + B.angle*angle + B.gmz*gmz + B.aim*aim
            + B.bigchance*(bc?1:0) + B.penalty*(pen?1:0) + B.oneone*(oo?1:0)
            + bPlayer;  // ← efecto de jugador
const xG = 1 / (1 + Math.exp(-logit));
```

---

## 🗂️ Archivos del Modelo

| Archivo | Descripción |
| :--- | :--- |
| `Modelo_1_Expected_Goals_V2.ipynb` | Pipeline completo: Punto de Partida → EDA → Candidatos → FE → VIF → Spearman → Entrenamiento → Resultados → Coeficientes → **Efectos de Jugador** |
