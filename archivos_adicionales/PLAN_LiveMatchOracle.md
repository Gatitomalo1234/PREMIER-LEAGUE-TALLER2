# Live Match Oracle — Plan de Implementación
**Nodo interactivo M2 + M3 · Dashboard Premier League ML**

---

## Concepto

Un simulador de partido que **emula** un encuentro — no lo transmite en vivo ni sigue una cronología real. El usuario configura el contexto pre-partido (cuotas + momentum), pulsa "Simular" y el Oracle genera un partido completo de forma instantánea: resultado, goles, eventos clave. Puede repetirlo infinitas veces cambiando los inputs. El foco es mostrar **cómo reaccionan M2 y M3 en tiempo real** ante distintos escenarios tácticos.

---

## Variables disponibles (solo las del modelo real)

### M3 — Regresión Logística Multinomial
**Features:** `b365h`, `b365a`, `home_pts_last3`, `home_ga_last3`  
**Output:** P(H), P(D), P(A) — probabilidades de victoria local / empate / victoria visitante  
**Preprocesamiento:** StandardScaler (means y scales embebidos como constantes JS)  
**Clases:** A=0, D=1, H=2 (orden sklearn)

### M2 — Regresión Lasso
**Features:** `Home_Sum_influence`, `Away_Avg_AST`, `Home_Avg_FTHG`, `Home_Days_Rest`  
**Output:** `log(goles+1)` → goles totales esperados  
**Ecuación:** `log(y+1) = 1.224 + 0.070·INF + 0.041·AST − 0.060·FTHG − 0.050·REST`

> **Nota:** M2 y M3 usan features distintas. El Oracle los corre en paralelo con sus respectivos inputs. Donde no haya overlap exacto, se usan aproximaciones derivadas de los sliders (documentadas abajo).

---

## Arquitectura de pantalla

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ INTRO FLASH  →  reveal animado con GSAP spring         │
├──────────────────────┬──────────────────────────────────────┤
│  SELECTOR DE PARTIDO │  Arsenal  vs  Manchester City        │
│  (6 fixtures reales) │  Jornada 24 · Emirates Stadium       │
├──────────────────────┴──────────────────────────────────────┤
│                                                             │
│  PANEL INPUTS (sliders en tiempo real)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Cuota Local (B365H)      ──●──────  2.40            │   │
│  │ Cuota Visitante (B365A)  ────────●  3.10            │   │
│  │ Pts últimas 3 (local)    ────●───   6 pts           │   │
│  │ Goles visita recientes   ──●──────  1.2 /partido    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  M3 — PROBABILIDADES  (recalcula en cada cambio de slider)  │
│                                                             │
│  LOCAL    ████████████░░░░░░  48%  ←→ anima con GSAP       │
│  EMPATE   ██████░░░░░░░░░░░░  28%                          │
│  VISITA   █████░░░░░░░░░░░░░  24%                          │
│                                                             │
│  "El modelo ve valor en el local — cuota 2.40              │
│   implícita 41.7%, modelo asigna 48%"                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  M2 — GOLES TOTALES ESPERADOS                               │
│                                                             │
│        ◉  2.4                                              │
│   [gauge circular animado]                                  │
│   "Partido cerrado · Under 2.5 probable"                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  BOTÓN PRINCIPAL                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ⚡  SIMULAR PARTIDO                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  RESULTADO DE SIMULACIÓN (aparece tras el botón)            │
│                                                             │
│  Arsenal  2 - 1  Manchester City                            │
│                                                             │
│  Eventos generados:                                         │
│  23'  ⚽ Gol local  →  P(H) sube a 61%  │  M2: 2.8 goles  │
│  67'  ⚽ Gol visita →  P(H) baja a 52%  │  M2: 3.1 goles  │
│  71'  ⚽ Gol local  →  P(H) sube a 68%  │  M2: 3.4 goles  │
│                                                             │
│  Veredicto final del Oracle:                               │
│  "M3 acertó — predijo H con 48%, ocurrió H (2-1)"         │
│                                                             │
│  [ 🔄 SIMULAR OTRA VEZ ]  [ ✏️ CAMBIAR ESCENARIO ]        │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de interacción

### Fase 1 — Configuración
El usuario ajusta 4 sliders con rangos reales del dataset:

| Slider | Rango | Default | Feature que alimenta |
|--------|-------|---------|----------------------|
| Cuota local (B365H) | 1.30 – 8.00 | 2.50 | M3: `b365h` |
| Cuota visitante (B365A) | 1.30 – 8.00 | 3.20 | M3: `b365a` |
| Puntos local (últimas 3J) | 0 – 9 | 5 | M3: `home_pts_last3` |
| Goles visita/partido (rec.) | 0.5 – 3.5 | 1.38 | M3: `away_gf_last3` |

M2 usa approximaciones derivadas:
- `Home_Avg_FTHG` ← derivado de cuota local (equipos con cuota baja tienen historial goleador)
- `Away_Avg_AST` ← derivado de `away_gf_last3` × 2.5 (ratio tiros/goles del dataset)
- `Home_Days_Rest` ← valor fijo neutro (7 días, promedio PL)
- `Home_Sum_influence` ← derivado de `home_pts_last3` × factor FPL calibrado

**En cada cambio de slider:** M3 y M2 recalculan instantáneamente. Las barras y el gauge animan suavemente con GSAP `duration: 0.4, ease: "power2.out"`.

### Fase 2 — Simulación
Al pulsar "Simular":

1. **Flash + sonido** — destello cyan + primeros 0.5s del audio de crowd
2. **Generación del partido** — algoritmo de simulación basado en los outputs de los modelos (ver abajo)
3. **Replay de eventos** — los 2–4 eventos aparecen uno a uno con stagger de 800ms, y en cada evento las barras de M3 y el gauge de M2 re-animan al nuevo estado
4. **Veredicto** — el resultado real se compara con la predicción de M3 y aparece el audio (Closs si acertó, Bambino si falló)

### Fase 3 — Replay o cambio de escenario
Dos botones: repetir con mismos inputs (nueva simulación aleatoria) o resetear sliders.

---

## Algoritmo de simulación del partido

```javascript
function simulateMatch(p_home, p_draw, p_away, expected_goals) {
  // 1. Decidir resultado basado en probabilidades M3
  const result = weightedPick(['H','D','A'], [p_home, p_draw, p_away]);

  // 2. Generar goles consistentes con M2 y el resultado
  const totalGoals = poissonSample(expected_goals);  // Poisson(λ=M2)
  const [homeGoals, awayGoals] = splitGoals(totalGoals, result);

  // 3. Generar minutos de los goles (distribución uniforme + sesgo final)
  const events = generateMatchEvents(homeGoals, awayGoals);

  // 4. Para cada evento, recalcular M3 con deltas calibrados
  const timeline = events.map((evt, i) => ({
    ...evt,
    m3_after: recalcM3AfterEvent(p_home, p_draw, p_away, evt, i, events.length),
    m2_after: recalcM2AfterEvent(expected_goals, evt)
  }));

  return { result, homeGoals, awayGoals, timeline };
}
```

### Deltas de eventos sobre M3 (calibrados con lógica del modelo)

| Evento | Δ P(H) | Δ P(D) | Δ P(A) | Δ M2 |
|--------|--------|--------|--------|------|
| Gol local | +0.10 a +0.18 | −0.04 | −0.08 | +0.25 |
| Gol visitante | −0.10 a −0.15 | −0.04 | +0.12 | +0.25 |
| Gol local (minuto >75') | +0.18 a +0.25 | −0.06 | −0.15 | +0.1 |
| Gol visitante (min >75') | −0.18 a −0.25 | −0.06 | +0.20 | +0.1 |

Los deltas se normalizan siempre para que P(H)+P(D)+P(A)=1.

---

## Coeficientes a embeber (extraídos del notebook)

### M3 — StandardScaler params
Se extraen de `scaler.mean_` y `scaler.scale_` tras correr el notebook:
```javascript
const M3_SCALER = {
  means:  [/* b365h_μ, b365a_μ, home_pts_μ, away_gf_μ */],
  scales: [/* b365h_σ, b365a_σ, home_pts_σ, away_gf_σ */]
};
// Orden features: b365h, b365a, home_pts_last3, away_gf_last3
// Clases orden sklearn: A=0, D=1, H=2
const M3_COEFS = [
  [/* coef clase A: b365h, b365a, home_pts, away_gf */],
  [/* coef clase D */],
  [/* coef clase H */]
];
const M3_INTERCEPTS = [/* intercept A, D, H */];
```

### M2 — Lasso (ya disponibles)
```javascript
const M2 = {
  intercept: 1.224,
  b_influence: 0.070,   // Home_Sum_influence
  b_ast:       0.041,   // Away_Avg_AST
  b_fthg:     -0.060,   // Home_Avg_FTHG
  b_rest:     -0.050    // Home_Days_Rest
};
```

**Paso pendiente:** Correr una vez el notebook de M3, agregar al final:
```python
print("SCALER MEANS:", scaler.mean_.tolist())
print("SCALER SCALES:", scaler.scale_.tolist())
print("COEFS:", clf.coef_.tolist())
print("INTERCEPTS:", clf.intercept_.tolist())
```
Y copiar los valores al JS.

---

## Diseño visual — tokens

Hereda 100% el design system existente del dashboard:

| Token | Valor | Uso |
|-------|-------|-----|
| `--cyan` | `#00ffff` | Gol local, P(H), gauge positivo |
| `--magenta` | `#ff44ff` | Gol visitante, P(A), acciones |
| `--gold` | `#ffcc00` | Empate, P(D), eventos neutros |
| `--red` | `#ff4444` | Tarjeta, penalti, alerta |
| Glass base | `rgba(255,255,255,.04)` + `backdrop-filter:blur(8px)` | Cards, sliders, barras |
| Border | `1px solid rgba(255,255,255,.08)` | Todos los contenedores |

### Animaciones GSAP — secuencias clave

**Entrada del nodo (wow moment):**
```javascript
// 1. Flash de estadio
gsap.fromTo('#oracle-flash', {opacity:0.8}, {opacity:0, duration:0.4, ease:'power2.out'})
// 2. Scoreboard cae con rebote
gsap.from('#oracle-scoreboard', {y:-80, opacity:0, duration:0.7,
  ease:'back.out(1.4)', delay:0.2})
// 3. Sliders entran en stagger
gsap.from('.oracle-slider', {x:-30, opacity:0, duration:0.4,
  stagger:0.08, ease:'power2.out', delay:0.5})
// 4. Barras M3 se "cargan" de izquierda a derecha
gsap.from('.m3-bar-fill', {width:'0%', duration:0.8,
  stagger:0.12, ease:'power3.out', delay:0.8})
// 5. Gauge M3 gira al valor inicial
gsap.to('#m2-gauge-arc', {strokeDashoffset: calcOffset(m2Value),
  duration:1.0, ease:'power2.out', delay:0.9})
```

**Al cambiar un slider (reactividad instantánea):**
```javascript
// Debounce 80ms para no saturar
gsap.to('.m3-bar-fill', {width: newPct+'%', duration:0.35, ease:'power2.out'})
gsap.to('#m2-gauge-arc', {strokeDashoffset: newOffset, duration:0.35, ease:'power2.out'})
```

**Al aparecer cada evento del partido:**
```javascript
// Slide-in desde izquierda
gsap.from(eventEl, {x:-20, opacity:0, duration:0.3, ease:'power2.out'})
// Flash en las barras afectadas
gsap.to(barEl, {backgroundColor: flashColor, duration:0.15,
  yoyo:true, repeat:1})
```

---

## Selector de fixtures

6 partidos reales del dataset con sus probabilidades base pre-calculadas:

| Fixture | B365H | B365A | Pts Local | Goles Visita | P(H) | P(D) | P(A) | M2 |
|---------|-------|-------|-----------|--------------|------|------|------|-----|
| Arsenal vs Man City | 2.40 | 3.10 | 6 | 1.2 | ~42% | ~28% | ~30% | 2.4 |
| Liverpool vs Chelsea | 1.90 | 4.20 | 7 | 1.5 | ~52% | ~26% | ~22% | 2.7 |
| Man Utd vs Tottenham | 3.20 | 2.40 | 3 | 1.8 | ~28% | ~28% | ~44% | 2.6 |
| Aston Villa vs Newcastle | 2.10 | 3.60 | 5 | 1.1 | ~46% | ~28% | ~26% | 2.2 |
| Brighton vs Brentford | 2.60 | 2.90 | 4 | 1.4 | ~38% | ~30% | ~32% | 2.5 |
| Fulham vs Bournemouth | 2.20 | 3.40 | 5 | 1.0 | ~44% | ~28% | ~28% | 2.1 |

> Los valores exactos de P(H/D/A) y M2 se calculan en runtime con los modelos embebidos, estos son orientativos.

---

## Mensajes contextuales del Oracle

El panel genera una frase interpretativa que cambia con cada recalculo:

### M3 — frases según escenario
```
P(H) > 55%:  "El modelo ve ventaja clara del local — cuota implícita subestima al favorito"
P(H) 45-55%: "Partido parejo — cuotas y momentum apuntan al local por poco"
P(D) > 35%:  "Alta probabilidad de empate — momentum bajo de ambos equipos"
P(A) > 45%:  "El visitante es favorito pese a jugar fuera — momentum reciente lo respalda"
```

### M2 — frases según goles esperados
```
< 2.0:  "Partido muy cerrado — ambas defensas sólidas, Under 2.5 seguro"
2.0–2.5: "Partido equilibrado — Under 2.5 ligero favorito"
2.5–3.2: "Se esperan goles — Over 2.5 probable"
> 3.2:  "Partido abierto — ambos ataques en forma, Over 3.5 posible"
```

---

## Audio integrado

Reutiliza los tres archivos ya existentes:

| Momento | Audio | Descripción |
|---------|-------|-------------|
| Apertura del nodo | `closs_gol.mp3` (primeros 1.5s, muted fade-in) | Rugido de multitud |
| Simulación — gol generado | `closs_gol_short.mp3` trigger +7s | Closs grita GOL |
| Simulación — M3 acertó | `closs_gol_short.mp3` | Celebración |
| Simulación — M3 falló | `closs_uhh_short.m4a` trigger +1.8s | Bambino reacciona |
| Tiro fallado (xG bajo) | `fallo_final.m4a` | Narración de fallo |

---

## Estructura de archivos a crear

```
dashboard.html          ← WS['live']['predictions'] — contenido del tab
                        ← WS['live']['overview']   — ya existe (placeholder)
                        ← JS block: window._liveOracleInit()
                        ← CSS en <head>: .oracle-*, .m3-bar-*, .m2-gauge-*
```

Todo va embebido en el `dashboard.html` existente, sin archivos externos adicionales.

---

## Orden de implementación

1. **Extraer coeficientes** — correr 3 líneas extra en el notebook de M3, copiar valores
2. **CSS** — agregar tokens `.oracle-*` al `<head>` del dashboard
3. **HTML** — escribir `WS['live']['predictions']` con la estructura completa
4. **JS modelo** — funciones `m3Predict()`, `m2Predict()`, `simulateMatch()`
5. **JS animaciones** — `_liveOracleInit()` con secuencia GSAP de entrada
6. **JS sliders** — listeners con debounce 80ms → recalculo → animación
7. **JS simulación** — `runSimulation()` → timeline → replay de eventos
8. **Audio** — reutilizar `playGoalSound` / `playMissAudio` ya implementados
9. **QA** — verificar que el tab switch no rompa el estado del Oracle

---

## Criterio de éxito

- Los sliders recalculan M3 y M2 en < 16ms (sin GSAP delay)
- La animación de entrada hace decir "wow" en los primeros 1.5s
- Una simulación completa con 3 eventos tarda < 4s en reproducirse
- M3 usa los coeficientes reales del modelo entrenado, no aproximaciones
- El panel funciona sin conexión a internet (todo embebido)
