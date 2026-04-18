import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Load the data
df = pd.read_csv('/Users/nicolas/Documents/MACHINE LEARNING /TALLER 2/data/xg_train.csv')

# Features based on the README
features = ['dist_al_arco', 'angulo_tiro', 'is_BigChance', 'is_Penalty', 'is_OneOnOne', 'threat']
X = df[features]
y = df['is_goal']

# Standardize Continuous Variables (dist_al_arco, angulo_tiro, threat)
scaler = StandardScaler()
X_scaled = X.copy()
# We should probably not scale binary variables to keep the exp(beta) interpretation easy: "If it is a BigChance..."
# Actually, the original model from the student might have scaled everything. Let's assume standard scaler for continuous.
X_scaled[['dist_al_arco', 'angulo_tiro', 'threat']] = scaler.fit_transform(X[['dist_al_arco', 'angulo_tiro', 'threat']])

# Train model mimicking the README
clf = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
clf.fit(X_scaled, y)

# Calculate exp(beta)
print("--- COEFICIENTES LOGISTIC REGRESSION ---")
for feat, coef in zip(features, clf.coef_[0]):
    print(f"Feature: {feat.ljust(15)} | Beta: {coef:>6.3f} | exp(Beta): {np.exp(coef):>6.3f}")
print("Interceptor (Beta 0):", clf.intercept_[0])
