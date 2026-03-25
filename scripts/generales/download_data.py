import os
import requests
import pandas as pd
import time

BASE_URL = "https://premier.72-60-245-2.sslip.io"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def download_export(endpoint, filename):
    url = f"{BASE_URL}{endpoint}"
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Descargando {url} en {filepath}...")
    start_time = time.time()
    
    try:
        df = pd.read_csv(url)
        df.to_csv(filepath, index=False)
        elapsed = time.time() - start_time
        print(f"✓ Descarga exitosa de {filename}: {len(df)} filas obtenidas en {elapsed:.2f} segundos.")
    except Exception as e:
        print(f"✗ Error al descargar {filename}: {e}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    print("Iniciando descargas masivas...")
    download_export("/export/players", "players.csv")
    download_export("/export/matches", "matches.csv")
    download_export("/export/events", "events.csv")
    print("Descargas completadas.")

if __name__ == "__main__":
    main()
