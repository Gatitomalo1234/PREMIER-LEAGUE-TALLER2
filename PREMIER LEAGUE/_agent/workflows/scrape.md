---
description: Automatizar el scraping y procesamiento de datos de WhoScored
---

Sigue estos pasos para procesar un nuevo partido:

1. **Guardar el HTML del partido**:
   Ve al partido en WhoScored.com y guarda la página como "Página web completa" (.html) dentro de la carpeta `data/raw/whoscored/`.

2. **Ejecutar el Scraping**:
   Reemplaza `nombre_archivo.html` con el nombre del archivo que guardaste.
   // turbo
   ```bash
   python3 scripts/scrape_whoscored.py "data/raw/whoscored/nombre_archivo.html"
   ```

3. **Procesar a CSV**:
   El paso anterior generó un JSON en `data/raw/whoscored/match_XXXX.json`. Reemplaza el ID correspondiente.
   // turbo
   ```bash
   python3 scripts/process_events.py data/raw/whoscored/match_XXXXXX.json
   ```

4. **Verificar Resultados**:
   Revisa los nuevos archivos generados en la carpeta `data/processed/`.
