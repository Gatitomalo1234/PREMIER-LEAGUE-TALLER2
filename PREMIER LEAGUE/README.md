# Proyecto Premier League 2025-26

Este proyecto extrae, procesa y organiza datos de la Premier League temporada 2025-26 desde tres fuentes fundamentales: **FPL**, **football-data.co.uk** y **WhoScored**.

## 📁 Estructura del Proyecto

```text
PREMIER LEAGUE/
├── data/
│   ├── raw/                # Datos originales (sin modificar)
│   │   ├── football-data/  # CSV de resultados y cuotas (E0.csv)
│   │   ├── whoscored/      # JSONs y HTMLs descargados de WhoScored
│   │   └── fpl/            # JSON masivo de la API de FPL
│   └── processed/          # CSVs procesados listos para análisis de ML
├── scripts/                # Scripts de automatización (Python)
│   ├── extract_data.py     # Baja datos de FPL y football-data
│   ├── scrape_whoscored.py # Extrae eventos de WhoScored (Playwright)
│   └── process_events.py   # Convierte JSON de WhoScored a CSVs limpios
├── guia-ml1-premier-league-data.pdf # Guía metodológica del taller
├── README.md               # Documentación general
└── venv/                   # Entorno virtual de Python
```

---

## 🚀 Guía de Uso

### 1. Preparar el Entorno
Sigue estos pasos para crear tu entorno virtual e instalar las dependencias:
```bash
python3 -m venv venv        # Crear entorno virtual
source venv/bin/activate    # Activar (Mac/Linux)
# venv\Scripts\activate     # Activar (Windows)

pip install -r requirements.txt
playwright install chromium
```

### 2. Descarga de Datos Generales (FPL & Football-Data)
Ejecuta el script para obtener los resultados básicos y la base de datos de jugadores:
```bash
python scripts/extract_data.py
```
> Los archivos se guardarán en `data/raw/fpl/` y `data/raw/football-data/`.

### 3. Extraer Eventos de WhoScored (Scraping)
Para obtener pases, tiros y eventos detallados con coordenadas (x, y):
1. **Recomendado:** Ve al partido en WhoScored.com y guarda la página como "Página web completa" (.html) en `data/raw/whoscored/`.
2. Ejecuta el extractor sobre ese archivo:
   ```bash
   python scripts/scrape_whoscored.py "data/raw/whoscored/nombre_archivo.html"
   ```

### 4. Procesar Datos a CSV
Una vez tengas el JSON del partido, procésalo para generar los CSVs de eventos y jugadores:
```bash
python scripts/process_events.py data/raw/whoscored/match_XXXXX.json
```
> Esto generará 3 archivos en `data/processed/`: eventos, estadísticas de jugadores y estadísticas de equipo.

---

## 📊 Fuentes de Datos

| Fuente | ¿Qué responde? | Granularidad |
|---|---|---|
| **FPL API** | ¿Quién rinde? | Jugador (temporada) |
| **football-data** | ¿Qué pasó? | Partido (agregado) |
| **WhoScored** | ¿Cómo pasó? | Evento (por acción) |
