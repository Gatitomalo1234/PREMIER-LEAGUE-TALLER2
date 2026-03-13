"""
process_events.py
Procesa la lista COMPLETA de eventos (pases, tiros, etc.) de WhoScored.
Genera archivos con nombres descriptivos del partido.
"""
import sys
import json
import os
import re
import pandas as pd


def sanitize(name):
    """Limpia el nombre del equipo para usarlo en un nombre de archivo."""
    name = name.replace(" ", "_")
    return re.sub(r'[^a-zA-Z0-9_]', '', name)


def flatten_all_events(match_data):
    """Aplana la lista 'events' (todas las acciones) en un DataFrame."""
    mcd = match_data['matchCentreData']
    events = mcd.get('events', [])
    
    match_id = match_data.get('matchId')
    home_team = mcd['home'].get('name', mcd['home'].get('teamName', ''))
    away_team = mcd['away'].get('name', mcd['away'].get('teamName', ''))
    home_id = mcd['home'].get('teamId')
    
    player_names = mcd.get('playerIdNameDictionary', {})
    
    all_rows = []
    for ev in events:
        side = 'home' if ev.get('teamId') == home_id else 'away'
        team_name = home_team if side == 'home' else away_team
        
        row = {
            'matchId': match_id,
            'homeTeam': home_team,
            'awayTeam': away_team,
            'side': side,
            'teamName': team_name,
            'eventId': ev.get('eventId'),
            'playerId': ev.get('playerId'),
            'playerName': player_names.get(str(ev.get('playerId', '')), ''),
            'minute': ev.get('minute'),
            'second': ev.get('second'),
            'x': ev.get('x'),
            'y': ev.get('y'),
            'period': ev.get('period', {}).get('displayName', ''),
            'type': ev.get('type', {}).get('displayName', ''),
            'outcomeType': ev.get('outcomeType', {}).get('displayName', ''),
        }
        
        qualifiers = ev.get('qualifiers', [])
        qual_list = []
        for q in qualifiers:
            q_name = q.get('type', {}).get('displayName', '')
            q_val = q.get('value', True)
            qual_list.append(q_name)
            if q_name == 'PassEndX': row['endX'] = q_val
            elif q_name == 'PassEndY': row['endY'] = q_val
            elif q_name == 'Angle': row['angle'] = q_val
            elif q_name == 'Length': row['length'] = q_val
            
        row['qualifiers'] = ', '.join(qual_list)
        all_rows.append(row)
        
    return pd.DataFrame(all_rows)

def extract_player_stats(match_data):
    """Extrae las estadísticas individuales de cada jugador."""
    mcd = match_data['matchCentreData']
    match_id = match_data.get('matchId')
    home_team = mcd['home'].get('name', mcd['home'].get('teamName', ''))
    away_team = mcd['away'].get('name', mcd['away'].get('teamName', ''))
    
    all_players = []
    for side, team_key in [('home', 'home'), ('away', 'away')]:
        team = mcd[team_key]
        team_name = home_team if side == 'home' else away_team
        players = team.get('players', [])
        for p in players:
            row = {
                'matchId': match_id,
                'side': side,
                'teamName': team_name,
                'playerId': p.get('playerId'),
                'name': p.get('name', ''),
                'position': p.get('position', ''),
                'isFirstEleven': p.get('isFirstEleven', False),
            }
            stats = p.get('stats', {})
            for k, v in stats.items():
                if isinstance(v, (int, float)): row[k] = v
            all_players.append(row)
    return pd.DataFrame(all_players)

def extract_team_stats(match_data):
    """Extrae estadísticas a nivel de equipo."""
    mcd = match_data['matchCentreData']
    match_id = match_data.get('matchId')
    rows = []
    for side in ['home', 'away']:
        team = mcd[side]
        team_name = team.get('name', team.get('teamName', ''))
        stats = team.get('stats', {})
        row = {'matchId': match_id, 'side': side, 'teamName': team_name}
        for k, v in stats.items():
            if isinstance(v, (int, float)): row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    if len(sys.argv) < 2: sys.exit(1)
    json_path = sys.argv[1]
    with open(json_path, 'r') as f: data = json.load(f)
    
    mcd = data['matchCentreData']
    home_name = sanitize(mcd['home'].get('name', mcd['home'].get('teamName', 'Home')))
    away_name = sanitize(mcd['away'].get('name', mcd['away'].get('teamName', 'Away')))
    
    season = "2025_26"
    prefix = f"{home_name}_vs_{away_name}_{season}"
    
    os.makedirs('data/processed', exist_ok=True)
    
    # 1. Eventos
    df_events = flatten_all_events(data)
    df_events.to_csv(f'data/processed/{prefix}_events.csv', index=False)
    
    # 2. Jugadores
    df_players = extract_player_stats(data)
    df_players.to_csv(f'data/processed/{prefix}_players.csv', index=False)
    
    # 3. Equipo
    df_team = extract_team_stats(data)
    df_team.to_csv(f'data/processed/{prefix}_team_stats.csv', index=False)
    
    print(f"✅ Procesado completado para {prefix}")
    print(f"   Archivos generados en data/processed/:")
    print(f"   - {prefix}_events.csv")
    print(f"   - {prefix}_players.csv")
    print(f"   - {prefix}_team_stats.csv")

if __name__ == "__main__":
    main()
