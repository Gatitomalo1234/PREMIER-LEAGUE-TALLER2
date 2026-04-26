import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler

# Load data
matches = pd.read_csv('data/matches.csv')
matches['date_dt'] = pd.to_datetime(matches['date'], dayfirst=True)
matches = matches.dropna(subset=['date_dt']).sort_values('date_dt').reset_index(drop=True)

# --- FEATURE ENGINEERING (Anti-Leakage) ---
PRIOR_PTS = 1.30
PRIOR_GOALS = 1.38
N_WINDOW = 3

team_hist = {}
records = []
for _, row in matches.iterrows():
    home, away = row['home_team'], row['away_team']
    h_hist = team_hist.get(home, [])[-N_WINDOW:]
    a_hist = team_hist.get(away, [])[-N_WINDOW:]
    def avg(hist, key, prior): return float(np.mean([x[key] for x in hist])) if hist else prior
    
    records.append({
        'home_pts_last3': avg(h_hist, 'pts', PRIOR_PTS),
        'home_gf_last3': avg(h_hist, 'gf', PRIOR_GOALS),
        'home_ga_last3': avg(h_hist, 'ga', PRIOR_GOALS),
        'away_pts_last3': avg(a_hist, 'pts', PRIOR_PTS),
        'away_gf_last3': avg(a_hist, 'gf', PRIOR_GOALS),
        'away_ga_last3': avg(a_hist, 'ga', PRIOR_GOALS),
        'H_fthg_cum': avg(team_hist.get(home, []), 'gf', PRIOR_GOALS), # Expanding
        'A_ast_cum': avg(team_hist.get(away, []), 'ast', 4.0),         # Expanding
        'A_ac_w7': avg(team_hist.get(away, [])[-7:], 'ac', 5.0),      # Rolling 7
        'A_as__w7': avg(team_hist.get(away, [])[-7:], 'as', 10.0),     # Rolling 7
        'gdiff_w7': avg(team_hist.get(home, [])[-7:], 'gdiff', 0.0),  # Rolling 7
    })
    
    ftr = row['ftr']
    hg, ag = int(row['fthg']), int(row['ftag'])
    ast = float(row['ast']) if 'ast' in row and not pd.isna(row['ast']) else 4.0
    ac = float(row['ac']) if 'ac' in row and not pd.isna(row['ac']) else 5.0
    as_ = float(row['as_']) if 'as_' in row and not pd.isna(row['as_']) else 10.0
    
    h_pts = 3 if ftr=='H' else (1 if ftr=='D' else 0)
    a_pts = 3 if ftr=='A' else (1 if ftr=='D' else 0)
    
    team_hist.setdefault(home, []).append({'pts': h_pts, 'gf': hg, 'ga': ag, 'gdiff': hg-ag, 'ast': float(row['hst']) if 'hst' in row else 4.0, 'ac': float(row['hc']) if 'hc' in row else 5.0, 'as': float(row['hs']) if 'hs' in row else 10.0})
    team_hist.setdefault(away, []).append({'pts': a_pts, 'gf': ag, 'ga': hg, 'gdiff': ag-hg, 'ast': float(row['ast']) if 'ast' in row else 4.0, 'ac': float(row['ac']) if 'ac' in row else 5.0, 'as': float(row['as_']) if 'as_' in row else 10.0})

rolling_df = pd.DataFrame(records, index=matches.index)
df_full = pd.concat([matches, rolling_df], axis=1).dropna(subset=['ftr', 'b365h', 'b365a', 'total_goals'])

# --- TRAIN M3 (Result) ---
# Features from README/Notebook: b365h, b365a, home_pts_last3, away_gf_last3
m3_feats = ['b365h', 'b365a', 'home_pts_last3', 'away_gf_last3']
X3 = df_full[m3_feats]
y3 = df_full['ftr']
scaler3 = StandardScaler()
X3_s = scaler3.fit_transform(X3)
clf3 = LogisticRegression(solver='lbfgs', class_weight='balanced', max_iter=2000)
clf3.fit(X3_s, y3)

# --- TRAIN M2 (Goals) ---
# Features from README: H_fthg_cum, A_ast_cum, A_ac_w7, A_as__w7, gdiff_w7
m2_feats = ['H_fthg_cum', 'A_ast_cum', 'A_ac_w7', 'A_as__w7', 'gdiff_w7']
X2 = df_full[m2_feats]
y2 = df_full['total_goals']
scaler2 = StandardScaler()
X2_s = scaler2.fit_transform(X2)
clf2 = LinearRegression()
clf2.fit(X2_s, y2)

# --- EXPORT TO JS ---
print("const ORACLE_MODELS = {")
print("  m3: {")
print(f"    classes: {list(clf3.classes_)},")
print(f"    features: {m3_feats},")
print(f"    means: {list(scaler3.mean_)},")
print(f"    scales: {list(scaler3.scale_)},")
print(f"    coefs: {clf3.coef_.tolist()},")
print(f"    intercepts: {clf3.intercept_.tolist()}")
print("  },")
print("  m2: {")
print(f"    features: {m2_feats},")
print(f"    means: {list(scaler2.mean_)},")
print(f"    scales: {list(scaler2.scale_)},")
print(f"    coefs: {clf2.coef_.tolist()},")
print(f"    intercept: {clf2.intercept_}")
print("  }")
print("};")
