import pandas as pd
import numpy as np
import os

print("1. Cargando datasets base...")
df = pd.read_csv('/Users/nicolas/Documents/MACHINE LEARNING /TALLER 2/data/matches.csv')
df_p = pd.read_csv('/Users/nicolas/Documents/MACHINE LEARNING /TALLER 2/data/players.csv')

print("2. Procesando Diccionario de Peligrosidad FPL (Threat)...")
# Mapeo de dicciones FPL vs Matches
team_map = {'Man Utd': 'Man United', 'Spurs': 'Tottenham'}
df_p['team'] = df_p['team'].replace(team_map)

# Sumar el Threat absoluto de toda la nómina
Team_Threats = df_p.groupby('team')['threat'].sum().to_dict()

print("3. Ordenando el Tiempo (Mecánica Anti-Data Leakage)...")
df['date_parsed'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df = df.sort_values(by=['date_parsed', 'time']).reset_index(drop=True)

# Arrays para las nuevas columnas predictoras
home_rolling_scored = []
home_rolling_conceded = []
home_rolling_sot = []

away_rolling_scored = []
away_rolling_conceded = []
away_rolling_sot = []

# Tracker Histórico Independiente (Diccionario)
team_history = {team: {'scored': [], 'conceded': [], 'sot': []} for team in pd.concat([df['home_team'], df['away_team']]).unique()}

print("4. Ejecutando Bucle de Medias Móviles Retrospectivas (Últimos 3 Partidos)...")
for idx, row in df.iterrows():
    ht = row['home_team']
    at = row['away_team']
    
    # Leer el pasado estricto del Equipo Local (Últimos 3 eventos)
    h_hist_s = team_history[ht]['scored'][-3:]
    h_hist_c = team_history[ht]['conceded'][-3:]
    h_hist_st = team_history[ht]['sot'][-3:]
    
    # Leer el pasado estricto del Equipo Visitante
    a_hist_s = team_history[at]['scored'][-3:]
    a_hist_c = team_history[at]['conceded'][-3:]
    a_hist_st = team_history[at]['sot'][-3:]
    
    # Calcular promedio e inyectarlo a la Fila Actual
    home_rolling_scored.append(np.mean(h_hist_s) if h_hist_s else 0)
    home_rolling_conceded.append(np.mean(h_hist_c) if h_hist_c else 0)
    home_rolling_sot.append(np.mean(h_hist_st) if h_hist_st else 0)
    
    away_rolling_scored.append(np.mean(a_hist_s) if a_hist_s else 0)
    away_rolling_conceded.append(np.mean(a_hist_c) if a_hist_c else 0)
    away_rolling_sot.append(np.mean(a_hist_st) if a_hist_st else 0)
    
    # REGLA DE ORO: Solo DESPUÉS de predecir la fila, se actualiza el Tracker con lo que pasó hoy.
    team_history[ht]['scored'].append(row['fthg'])
    team_history[ht]['conceded'].append(row['ftag'])
    team_history[ht]['sot'].append(row['hst']) # Usamos Tiros al Arco como proxy táctico
    
    team_history[at]['scored'].append(row['ftag'])
    team_history[at]['conceded'].append(row['fthg'])
    team_history[at]['sot'].append(row['ast'])

# Asignar Arrays al DataFrame
df['home_threat'] = df['home_team'].map(Team_Threats)
df['away_threat'] = df['away_team'].map(Team_Threats)

df['home_rol_L3_scored'] = home_rolling_scored
df['home_rol_L3_conceded'] = home_rolling_conceded
df['home_rol_L3_sot'] = home_rolling_sot

df['away_rol_L3_scored'] = away_rolling_scored
df['away_rol_L3_conceded'] = away_rolling_conceded
df['away_rol_L3_sot'] = away_rolling_sot

print("5. Aislando la Matriz X de Oro...")
# Las famosas 6 Columnas aprobadas (Y un extra de Goles a favor por solidez)
final_features = [
    'date', 'home_team', 'away_team', 'total_goals', 
    'home_threat', 'away_threat',
    'home_rol_L3_sot', 'away_rol_L3_sot',
    'home_rol_L3_conceded', 'away_rol_L3_conceded'
]

df_golden = df[final_features]

out_path = '/Users/nicolas/Documents/MACHINE LEARNING /TALLER 2/data/matches_golden_features.csv'
df_golden.to_csv(out_path, index=False)
print(f"\\n✅ EXITO ROTUNDO: Matriz de Oro pre-procesada y guardada en:\\n{out_path}")
print("\\nMuestra de las primeras 3 filas (Nuevas Variables Matemáticas):")
print(df_golden.head(3))
