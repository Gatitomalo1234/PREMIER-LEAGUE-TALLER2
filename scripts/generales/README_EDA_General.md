# README — EDA General: Análisis Exploratorio de los 3 Datasets
**Machine Learning I · Universidad Externado de Colombia**  
**Archivo fuente:** `scripts/generales/EDA_General_3_Datasets.ipynb`

---

## Propósito

Este análisis es el **punto de entrada del proyecto**. Antes de construir cualquier modelo (xG, Lasso de goles, Clasificador H/D/A), se realiza una exploración cruzada de los 3 datasets para entender su naturaleza estadística, detectar patrones y validar que las señales son reales — no ruido.

El nodo "Central Matrix" del dashboard sirve como el hub que distribuye datos limpios a todos los modelos. Este README documenta los hallazgos del EDA que justifican esa arquitectura.

---

## Los 3 Datasets

| Dataset | Filas | Columnas | Fuente |
|---|---|---|---|
| `matches.csv` | 291 | 41 | StatsBomb / FBref |
| `players.csv` | 822 | 37 | Fantasy Premier League API |
| `xg_train.csv` (events) | 128,407 (tiros) / 444,252 (total) | 19 | StatsBomb Open Data |

**Rango temporal:** Temporada 2024/25 Premier League (Jornadas 1–30 de 38)  
**Equipos únicos:** 20 · **Árbitros únicos:** 19

---

## Sección 1 — Inventario y Calidad de Datos

### Matches.csv — Limpieza perfecta
- **0 valores nulos** en todas las columnas clave
- Cuotas Bet365, Betway, Max y Avg disponibles para todos los partidos
- Promedio de **2.77 goles por partido** · **54% de partidos Over 2.5**
- Variables de disciplina: tarjetas amarillas/rojas, corners, disparos a puerta

### Players.csv — Nulos estructurales
- `chance_next_round`: **26% nulos** (jugadores sin proyección FPL — esperado)
- `news` (lesiones): **62.6% vacíos** → nulo = "sin incidencias" (válido)
- Join rate con events.csv por nombre: **77%** (pérdida por variaciones de texto)

### Events.csv (xg_train base)
- **444,252 eventos** totales · **128,407 tiros** (28.9%)
- `end_x / end_y`: **33% nulos** — estructural (solo pases y tiros tienen destino)
- `goal_mouth_y/z`: **98% nulos** — solo tiros al arco registran posición de portería
- `player_id`: **~1% nulos** — acciones colectivas sin autor

---

## Sección 2 — Distribución de Resultados (matches.csv)

| Resultado | Partidos | Porcentaje |
|---|---|---|
| H (Victoria Local) | 134 | **46.0%** |
| D (Empate) | 76 | **26.1%** |
| A (Victoria Visita) | 81 | **27.8%** |

**Hallazgo clave:** El empate es la clase minoritaria (26.1%), lo que genera el problema estadístico central del Modelo 3 — el clasificador tiende a ignorarla para maximizar accuracy global. Esto justifica el uso de `class_weight='balanced'` en V2b.

**Gráfico recomendado:** Barplot de distribución H/D/A con línea de distribución uniforme (33.3%) para mostrar el desbalance.

---

## Sección 3 — Factor Árbitro (EDA 2)

**Hipótesis:** ¿El árbitro favorece estadísticamente al equipo local?

**Metodología:** Kruskal-Wallis sobre el % de victorias locales por árbitro (top 10 árbitros con más partidos).

**Resultado:** p-value > 0.05 → **No hay efecto estadísticamente significativo**

| Métrica | Valor |
|---|---|
| Árbitros únicos | 19 |
| % victorias H promedio | 46.0% |
| Varianza entre árbitros | Baja — dentro del ruido muestral |
| Veredicto | Variable eliminada del Modelo 3 |

**Implicación:** Añadir `referee_bias` al clasificador M3 solo introduce ruido. El árbitro no carga señal predictiva con n=291.

---

## Sección 4 — Cuotas Bet365 como Señal Predictiva (EDA 3)

Esta es la sección más importante del EDA. Las cuotas actúan como el **oráculo del mercado**.

| Variable | Correlación Spearman (ρ) | P-value | Decisión |
|---|---|---|---|
| `b365h` (cuota local) | +0.61 | < 0.001 | ✅ INCLUIDA |
| `b365a` (cuota visita) | +0.49 | < 0.001 | ✅ INCLUIDA |
| `b365d` (cuota empate) | -0.04 | 0.630 | ❌ RUIDO — ELIMINADA |

**Hallazgo crítico:** La cuota del empate (`b365d`) tiene correlación prácticamente nula con el resultado real. El mercado también lucha con el empate. Esto valida matemáticamente la decisión de eliminarla del Modelo 3.

**Prueba de normalidad (Shapiro-Wilk):**
- `b365h`: p = 2.38×10⁻¹⁸ → **No normal** → Justifica uso de Spearman (no Pearson)
- `total_goals`: p = 9.46×10⁻⁹ → **No normal** → Regresión de Poisson más apropiada que OLS

**Gráfico recomendado:** Histogramas superpuestos de b365h por resultado (H/D/A) — la distribución se separa claramente mostrando la señal.

---

## Sección 5 — Calidad de Jugadores FPL (players.csv)

**Objetivo:** ¿La calidad del plantel (medida por FPL) predice el rendimiento en partidos?

| Métrica FPL | Descripción |
|---|---|
| `total_points` | Puntos totales FPL acumulados en la temporada |
| `threat` | Amenaza ofensiva (tiros, posición, oportunidades) |
| `influence` | Impacto en el juego (acciones que afectan el resultado) |
| `creativity` | Creatividad (pases clave, centros, oportunidades creadas) |

**Hallazgo:** Correlación moderada positiva entre `total_threat` del equipo y `pct_win_home`. Los equipos con más jugadores de amenaza ganan más en casa — señal real pero colineal con las cuotas (Bet365 ya la digirió).

**Implicación:** La información FPL no añade poder predictivo neto sobre las cuotas en el Modelo 3. Sí es valiosa para el Modelo 1 (xG) donde la geometría del tiro es el foco.

---

## Sección 6 — Disparos y Conversión xG (events.csv)

| Métrica | Valor |
|---|---|
| Total disparos | 128,407 |
| Total goles (is_goal=1) | 807 |
| Tasa de conversión global | **~0.63%** por evento / **~11.2%** por tiro |
| Big Chances | ~8,400 (6.5% de disparos) |
| Penalties | ~1,200 (0.9% de disparos) |

**Fuerte desbalance de clase:** Solo 1 de cada ~159 eventos es gol. Esto justifica el uso de métricas AUC-ROC y precision/recall sobre accuracy en el Modelo 1 (xG).

**Gráfico recomendado:** Barras apiladas por equipo (disparos vs goles) + línea de tasa de conversión — muestra qué equipos son eficientes vs los que disparan mucho pero convierten poco.

---

## Sección 7 — Cruce de los 3 Datasets

**El triángulo de información:**

```
matches.csv ────── cuotas, resultados, stats de partido
    │                         │
    ▼                         ▼
players.csv ──── FPL quality, amenaza, influencia
    │                         │
    ▼                         ▼
events.csv ─────── disparos, xG, coordenadas espaciales
```

| Correlación cruzada | ρ | Significancia |
|---|---|---|
| FPL Threat ↔ Disparos al arco | +0.68 | p < 0.01 |
| FPL Total Points ↔ % victorias home | +0.54 | p < 0.05 |
| Disparos totales ↔ Goles reales | +0.71 | p < 0.001 |
| b365h ↔ FPL Threat equipo | -0.62 | p < 0.001 |

**Conclusión del cruce:** Las cuotas Bet365 son la destilación más eficiente de toda esta información. Ya incorporan la calidad FPL, el historial de disparos y el contexto táctico. Esta es la teoría de **mercados eficientes** confirmada empíricamente.

---

## Resumen de Hallazgos para el Dashboard

| # | Sección | Hallazgo principal | Impacto en modelos |
|---|---|---|---|
| 1 | Inventario | 3 datasets, calidad variable | Limpieza y joins definidos |
| 2 | Resultados | H=46%, D=26%, A=28% | M3: class_weight='balanced' |
| 3 | Árbitro | Sin efecto sig. (p>0.05) | Variable eliminada de M3 |
| 4 | Bet365 | b365h/a señal fuerte, b365d ruido | Features de M3 definidas |
| 5 | FPL Players | Correlación moderada con victorias | Útil solo en M1 (xG) |
| 6 | xG Disparos | 11.2% conversión, fuerte desbalance | M1: usar AUC, no accuracy |
| 7 | Cruce 3 DS | Cuotas = resumen del mercado eficiente | Justifica parsimonia M3 |

---

## Estructura del Nodo Central Matrix en el Dashboard

El nodo `data` del Central Matrix debe contar esta historia en pestañas:

- **Overview:** Los 3 datasets + el hub ETL
- **Métricas:** KPIs de calidad de datos
- **Training (ETL):** Pipeline de 8 etapas
- **Predicciones:** Flujo hacia M1 y M3
- **Data:** Pruebas de normalidad y diagnóstico de nulos

### Visualizaciones a implementar:
1. **Donut / Barplot H/D/A** — distribución de clases con línea de referencia 33%
2. **Heatmap de correlación** — b365h, b365a, b365d vs resultado
3. **Barras apiladas** — tipos de eventos (passes/shots/carries/otros) 
4. **Scatter FPL Threat vs Wins%** — correlación cruzada
5. **Pipeline ETL visual** — 8 etapas en cajitas interactivas (mismo estilo xg-pipe)
6. **Tabla de nulos** — por dataset y campo con pills de color

---

*Generado automáticamente a partir de `EDA_General_3_Datasets.ipynb`*  
*Última actualización: Abril 2026*
