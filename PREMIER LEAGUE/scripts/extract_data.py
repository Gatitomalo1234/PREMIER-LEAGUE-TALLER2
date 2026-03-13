import requests
import json
import os

# Obtiene la ruta absoluta de la carpeta donde está este script (premier league)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def download_fpl_data():
    print("Descargando datos de la Fantasy Premier League...")
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Guarda el JSON completo en la misma ruta que este script
        filename = os.path.join(SCRIPT_DIR, 'fpl_data_2025_2026.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Éxito: Datos FPL descargados. ({len(data['elements'])} jugadores guardados en la carpeta premier league)")
    except Exception as e:
        print(f"❌ Error al descargar datos de FPL: {e}")

def download_football_data():
    print("\nDescargando datos CSV de football-data.co.uk (Premier League 25/26)...")
    # Es crucial usar http:// en lugar de https:// para evitar bloqueos por handshake SSL desde Python/Mac
    url = "http://www.football-data.co.uk/mmz4281/2526/E0.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    try:
        # Se agrega permitere_redirects y un timeout generoso
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Guarda el CSV en la misma ruta que este script
        filename = os.path.join(SCRIPT_DIR, 'premier_league_25_26_results.csv')
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"✅ Éxito: CSV de resultados guardado correctamente en la carpeta premier league")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de Conexión. Reintentar abriendo el enlace en tu navegador:")
        print(f"   -> {url}")
    except Exception as e:
        print(f"❌ Error al descargar CSV: {e}")

if __name__ == "__main__":
    download_fpl_data()
    download_football_data()
