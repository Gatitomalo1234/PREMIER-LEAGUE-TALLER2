# Modelo 2: Regresión Lineal (Predictor de Goles Totales)

Este documento contiene la bitácora analítica y estructural para la predicción del volumen exacto de goles de un partido (`total_goals`), utilizando estrictamente información previa al saque inicial para neutralizar por completo el **Data Leakage**.

## 📂 Estructura del Dataset Base (`matches.csv`)

A diferencia del Modelo 1 (donde microscópicamente analizamos cada evento y disparo), aquí el reto es macroscópico. Afortunadamente, durante nuestras audaces Fases 0 y 1 de Exploratory Data Analysis (EDA) conjuntas de días anteriores, ya auditamos este archivo de pies a cabeza con las siguientes conclusiones:

- **Volumen Analizado**: 291 partidos jugados × 41 atributos.
- **Pureza Extrema**: El dataset es de calidad quirúrgica (`0 nulos`, `0 duplicados`).
- **Target Continuo a Predecir**: Se reportan **2.77 goles (`total_goals`)** en promedio por partido. Cerca del 54% de las veces, un cotejo de la Premier League rompe la barrera del "Over 2.5".

### 📖 Diccionario de Datos Pre-Partido (Anti-Leakage)
El gran error en Machine Learning deportivo (Data Leakage) es usar estadísticas del partido (como "Tiros al Arco") para predecir **ese mismo partido**, porque el algoritmo haría trampa viajando al pasado. Las únicas variables originales puras y autorizadas para entrar a la Matriz `X` de este modelo (las únicas que se conocen antes del pitazo inicial) son:

**1. Metadatos del Encuentro (Logísticos):**
* `home_team` / `away_team`: Equipos protagonistas.
* `date` / `time`: Cronología del partido.
* `referee`: El Árbitro central asignado.

**2. Rentabilidades de Casas de Apuestas (Wisdom of Crowds):**
Las casas de apuestas como B365 gastan millones en algoritmos para deducir quién ganará, si llueve o hay lesionados. Ese conocimiento ya viene empacado en estas cuotas de apertura oficial:
* `b365h` / `b365d` / `b365a`: Cuota de **Bet365** a Victoria Local (`h`), Empate (`d`) y Visita (`a`).
* `bwh` / `bwd` / `bwa`: Equivalente ofertado por **Betway**.
* `maxh` / `maxd` / `maxa`: Cotización máxima ofrecida globalmente en el mercado bursátil abierto.
* `avgh` / `avgd` / `avga`: El promedio oficial global, ideal para filtrar ruidos financieros o estafas.
* `implied_prob_h/d/a`: La probabilidad matemática formal (0% a 100%) derivada a partir de las cuotas.

> [!NOTE]
> Cualquier otra variable post-partido (como `fthg`, `hst`, o `hf`) será usada en nuestro código más adelante ÚNICAMENTE para calcular históricos (Medias Móviles de jornadas pasadas), prohibiéndose su uso en la fila de su jornada actual.

## 📊 Fase 2 y 3: Análisis Univariado y Bivariado (Auditoría Profunda Pre-Partido)

Acatando el rigor científico, sometimos estas variables "legales" a un escrutinio paramétrico riguroso para medir su capacidad aislada de predecir la cantidad de Goles (`total_goals`):

### 1. Colapso de la Normalidad Paramétrica (Shapiro-Wilk)
Para que una Regresión Lineal Clásica alcance su eficacia óptima, idealmente el vector objetivo debe conformar una Campana de Gauss. Nuestra auditoría formal probó que el fútbol no obedece campanas simétricas:
* `total_goals`: $p-value = 9.46 \\times 10^{-9}$ (Rechazada)
* `b365h`, `b365d`, `b365a`: $p-values \\approx 10^{-19}$ (Rechazadas masivamente)
* `implied_prob_h`: $p-value = 6.13 \\times 10^{-4}$ (Rechazada)

**Diagnóstico Arquitectónico**: Dibujar una recta infinita para pronosticar un fenómeno con tanta asimetría producirá márgenes de error altísimos, pero la Regresión se construirá asumiendo su límite como *Baseline Numérico* académico.

### 2. Matriz de Correlación No Paramétrica (Spearman)
Al caer la normalidad, empleamos la correlación robusta de Spearman (Matriz generada en `img/corr_matrix_matches.png`). Buscamos descifrar la relación monótona entre las Inteligencias de Mercado pre-partido y el `total_goals` resultante. 

¡El hallazgo fue dramático y revelador!
* **Correlación base casi nula**: La cuota de victoria local (`b365h` = 0.002) no determina en absoluto si habrá muchos goles o pocos. Las casas de apuesta pre-partido saben *quién* va a ganar, pero esas columnas no tienen "guardada" la información de la masacre goleadora.
* **El oráculo del Empate (`b365d` = 0.065)**: De toda la base cruda, la variable de mayor impacto matemático fue la cuota ofertada por el empate. A menor cuota de empate (partido muy apretado e igualado defensivamente), drásticamente menos goles. A mayor cuota (desigualdad de plantillas brutal), lluvia de goles asegurada.

**CONCLUSIÓN CIENTÍFICA DEL EDA:**
La pobreza predictiva de las variables base ($r < 0.07$) justifica de manera irrebatible nuestra necesidad matemática de ejecutar la **Fase 8 (Feature Engineering)**. Para que la Regresión Lineal funcione, ESTAMOS OBLIGADOS a fabricar las Medias Móviles de Tiros al Arco y Goles Históricos, o de lo contrario el modelo morirá ciego.

### 3. Fase 3.5: Categóricas Crudas vs Goles (Kruskal-Wallis)
Para evaluar si las Etiquetas de Texto Puras (Nombres de Equipos o nombres de Árbitros) impactan intrínsecamente el volumen de goles, dibujamos Gráficos de Cajas (Boxplots visuales en `img/boxplots_categorical.png`) y los sometimos al estricto Test de Medianas de Kruskal-Wallis para variables ordinales cruzadas.

Los resultados aniquilaron cualquier suposición empírica:
1. **`home_team` (p-value = 0.8989):** El nombre de la franquicia local no altera significativamente la mediana global de goles de un partido en una temporada. (¡Aceptamos H0!).
2. **`away_team` (p-value = 0.0883):** Tampoco aporta significancia estadística dura como etiqueta cruda (>0.05).
3. **`referee` (p-value = 0.5301):** El mito del "Árbitro Goleador o Conservador" queda matemáticamente desmentido. El juez central es ruido estadístico absoluto.

🔥 **Impacto Arquitectónico Final:**
El nombre estático de un equipo no sirve para predecir. Lo que realmente predice es su **"Forma Fisiológica Actual"** (Moméntum de las últimas 3 semanas). Rechazamos oficialmente insertar dummies One-Hot Encoding de Equipos y Árbitros en la Regresión Lineal. 

---

## 🛠 Fase 8: Ingeniería de Variables (El "Golden Dataset")

Con la comprobación matemática tajante de que las variables básicas de `matches.csv` carecen de poder predictivo (EDA crudo), estructuramos una **Arquitectura de Variables de Élite** para la Regresión Lineal de Goles mediante nuestro script `scripts/modelo_2_partidos/create_match_features.py`.

Bajo la premisa inquebrantable de evitar el *Data Leakage*, hemos creado la **Matriz de Oro de 6 Variables**:

### 1. La Purga Definitiva (Limpieza de Ruido Blanco)
* **Adiós Cuotas de Apuestas**: Las variables de mercado (`b365`) fueron desechadas exclusivamente para el modelo de *Total_Goals* al comprobarse su ineficiencia (Spearman $\\approx 0.002$) y por violar supuestos de multicolinealidad.
* **Adiós Etiquetas Estáticas**: Árbitros y nombres de equipo fueron descartados de la regresión por no superar la prueba H0 de Kruskal-Wallis.

### 2. Dimensión FPL (Peligrosidad Teórica de Plantilla)
Mediante el cruce relacional profundo con el dataset `players.csv`, extrajimos la reputación ofensiva estructural antes del pitazo inicial:
1. **`home_threat`**: Suma total del índice de Peligrosidad FPL (*Threat*) de todos los integrantes del equipo local. (Nos avisa si un equipo es una "Máquina Ofensiva", independientemente de sus últimos resultados).
2. **`away_threat`**: Índice de peligro sumado equivalente de la escuadra visitante.

### 3. El Motor Cronológico Temporal (Moméntum Retrospectivo)
Haciendo a la Inteligencia Artificial viajar al pasado de la liga con *Rolling Means*, le inyectamos el pulso atlético (*Moméntum*) a nuestra predicción. Para el cotejo actual, buscamos y promediamos el rendimiento de cada franquicia en sus **últimos 3 encuentros**:
3. **`home_rol_L3_sot`** / **`away_rol_L3_sot`**: Promedio de tiros efectivos al arco recientes (El mejor Proxy paramétrico de las Ocasiones Manifiestas de Gol). Si un equipo llega pateando 15 veces al arco, los goles lloverán por mera probabilidad matemática.
4. **`home_rol_L3_conceded`** / **`away_rol_L3_conceded`**: Indicador letal de perforación defensiva. Cuántos goles están permitiendo atrás en rachas cortas. (Dos equipos débiles en defensa equivalen matemáticamente a un pronóstico alto de goles totales).

### 🏆 Entregable Final: `matches_golden_features.csv`
Este Pipeline de Inyección de Features fue ejecutado íntegramente emparejando FPL + Históricos Temporales, y exportó con éxito puro la tabla maestra de entrenamiento en la ruta `data/matches_golden_features.csv`.

#### 🔑 Diccionario Definitivo de Variables (Inputs del Modelo)
Esta tabla inmaculada quedó conformada al 100% por estas únicas columnas:

**Contexto y Target:**
* `date`: Fecha cronológica estricta del encuentro.
* `home_team` / `away_team`: Llaves categóricas referenciales.
* `total_goals`: Nuestra variable a predecir (**Target Continuo**).

**Las 6 Features Predictivas de Oro (La Matriz `X`):**
1. **`home_threat`** & **`away_threat`**: La sumatoria bruta de peligrosidad estructurada por el algoritmo oficial de Fantasy Premier League (FPL) para toda la plantilla del equipo. Evalúa el "Nivel de Terror" jerárquico que impone el roster por sí solo.
2. **`home_rol_L3_sot`** & **`away_rol_L3_sot`**: *Media Móvil* de Tiros al Arco acertados por el equipo en sus **últimos 3 encuentros**. Sirve como el medidor continuo de su maquinaria de "Creación de Oportunidades". Equipos con este número alto, irremediablemente causan partidos con muchos goles.
3. **`home_rol_L3_conceded`** & **`away_rol_L3_conceded`**: *Media Móvil* de Goles Recibidos en sus **últimas 3 apariciones**. Cuantifica matemáticamente la fragilidad actual y qué tan colapsada llega esa línea defensiva al pitazo inicial de hoy.

Esta matriz es la única dueña de los factores predictivos que no incurren en *Data Leakage*, limpiada y parametrizada con la exactitud metodológica requerida para alimentar el entrenamiento Lineal en la sesión futura.
