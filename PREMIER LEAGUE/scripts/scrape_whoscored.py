"""
scrape_whoscored.py
Extrae datos de eventos de partidos desde WhoScored usando Playwright.

Uso:
    python scripts/scrape_whoscored.py <URL>

Ejemplo:
    python scripts/scrape_whoscored.py "https://es.whoscored.com/matches/1903429/live/..."
"""
import sys
import json
import os
import re
from playwright.sync_api import sync_playwright


def extract_match_data_from_page(page):
    """
    Extrae el bloque de datos del partido evaluando JavaScript en el contexto
    de la página. WhoScored almacena los datos en una etiqueta <script> como:
        matchCentreData: { ... },
        matchCentreEventTypeJson: { ... },
        formationIdNameMappings: { ... }
    """
    data = page.evaluate("""() => {
        // Buscar en todos los scripts el bloque que contiene matchCentreData
        const scripts = document.querySelectorAll('script');
        for (const script of scripts) {
            const text = script.textContent;
            if (text && text.includes('matchCentreData')) {
                // Extraer matchId
                const matchIdMatch = text.match(/matchId\\s*:\\s*(\\d+)/);
                const matchId = matchIdMatch ? parseInt(matchIdMatch[1]) : null;
                
                // Extraer matchCentreData (es un JSON grande)
                const dataMatch = text.match(/matchCentreData\\s*:\\s*(\\{.+?\\})\\s*,\\s*matchCentreEventTypeJson/s);
                let matchCentreData = null;
                if (dataMatch) {
                    try { matchCentreData = JSON.parse(dataMatch[1]); } catch(e) {}
                }
                
                // Extraer matchCentreEventTypeJson
                const eventTypeMatch = text.match(/matchCentreEventTypeJson\\s*:\\s*(\\{.+?\\})\\s*,\\s*formationIdNameMappings/s);
                let matchCentreEventTypeJson = null;
                if (eventTypeMatch) {
                    try { matchCentreEventTypeJson = JSON.parse(eventTypeMatch[1]); } catch(e) {}
                }
                
                // Extraer formationIdNameMappings
                const formationMatch = text.match(/formationIdNameMappings\\s*:\\s*(\\{.+?\\})/s);
                let formationIdNameMappings = null;
                if (formationMatch) {
                    try { formationIdNameMappings = JSON.parse(formationMatch[1]); } catch(e) {}
                }
                
                if (matchCentreData) {
                    return {
                        matchId,
                        matchCentreData,
                        matchCentreEventTypeJson,
                        formationIdNameMappings
                    };
                }
            }
        }
        return null;
    }""")
    return data


def extract_match_data_from_html(html_path):
    """
    Extrae datos del partido desde un archivo HTML descargado localmente.
    Alternativa cuando Playwright no puede navegar al sitio.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Buscar el bloque que contiene matchCentreData
    match_id_m = re.search(r'matchId\s*:\s*(\d+)', text)
    match_id = int(match_id_m.group(1)) if match_id_m else None

    # Extraer matchCentreData
    data_m = re.search(
        r'matchCentreData\s*:\s*(\{.+?\})\s*,\s*matchCentreEventTypeJson',
        text, re.DOTALL
    )
    match_centre_data = json.loads(data_m.group(1)) if data_m else None

    # Extraer matchCentreEventTypeJson
    event_m = re.search(
        r'matchCentreEventTypeJson\s*:\s*(\{.+?\})\s*,\s*formationIdNameMappings',
        text, re.DOTALL
    )
    event_type_json = json.loads(event_m.group(1)) if event_m else None

    # Extraer formationIdNameMappings
    formation_m = re.search(
        r'formationIdNameMappings\s*:\s*(\{[^}]+\})',
        text
    )
    formation_mappings = json.loads(formation_m.group(1)) if formation_m else None

    return {
        'matchId': match_id,
        'matchCentreData': match_centre_data,
        'matchCentreEventTypeJson': event_type_json,
        'formationIdNameMappings': formation_mappings
    }


def main():
    url = None
    html_file = None

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.endswith('.html'):
            html_file = arg
        else:
            url = arg
    else:
        url = "https://es.whoscored.com/matches/1903429/live/inglaterra-premier-league-2025-2026-manchester-city-nottingham-forest"

    os.makedirs('data/raw/whoscored', exist_ok=True)

    if html_file:
        # --- Modo local: extraer del HTML descargado ---
        print(f"Extrayendo datos desde archivo HTML local: {html_file}")
        data = extract_match_data_from_html(html_file)
    else:
        # --- Modo online: usar Playwright ---
        print(f"Iniciando scraping para: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            print("Cargando la página (esto puede tomar 30-60 segundos)...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            print("Página cargada. Extrayendo datos...")
            data = extract_match_data_from_page(page)
            browser.close()

    if data and data.get('matchCentreData'):
        match_id = data.get('matchId', 'unknown')
        out_file = f'data/raw/whoscored/match_{match_id}.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Datos extraídos exitosamente → {out_file}")
        print(f"   Match ID: {match_id}")
        mcd = data['matchCentreData']
        home = mcd.get('home', {}).get('teamName', '?')
        away = mcd.get('away', {}).get('teamName', '?')
        print(f"   Partido: {home} vs {away}")
        home_events = len(mcd.get('home', {}).get('incidentEvents', []))
        away_events = len(mcd.get('away', {}).get('incidentEvents', []))
        print(f"   Eventos encontrados: {home_events} (local) + {away_events} (visitante)")
    else:
        print("❌ No se pudieron extraer los datos. Posible bloqueo del sitio.")
        print("   Intenta descargar la página como HTML y usa:")
        print('   python scripts/scrape_whoscored.py "archivo.html"')
        sys.exit(1)


if __name__ == "__main__":
    main()
