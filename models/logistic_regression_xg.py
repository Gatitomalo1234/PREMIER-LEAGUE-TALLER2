import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score

def train_xg_model():
    print("=====================================================")
    print(" Entrenando Modelo de Expected Goals (xG) - Logística")
    print("=====================================================\n")
    
    # 1. Resolución segura de la ruta del dataset
    # Permite que ejecutemos el script tanto desde la raíz del proyecto como desde dentro de /models
    if os.path.exists('data/xg_train.csv'):
        data_path = 'data/xg_train.csv'
        out_path_img = 'img/roc_curve_xg.png' # Guardar imagen en la carpeta img
    elif os.path.exists('../data/xg_train.csv'):
        data_path = '../data/xg_train.csv'
        out_path_img = '../img/roc_curve_xg.png'
    else:
        raise FileNotFoundError("No se encontró el archivo 'xg_train.csv'. Asegúrate de estar en el directorio correcto.")

    print(f"1. Cargando datos desde: {data_path}...")
    df = pd.read_csv(data_path)
    
    # 2. Definición de variables
    target = 'is_goal'
    y = df[target]
    
    # Eliminar target y la columna de texto 'player_name' que fue conservada según el README
    cols_to_drop = [target]
    if 'player_name' in df.columns:
        cols_to_drop.append('player_name')
        
    X = df.drop(columns=cols_to_drop)
    
    print("2. Dividiendo los datos estratificados (80% Train / 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("3. Configurando modelo de Regresión Logística...")
    # max_iter alto para asegurar la convergencia
    model = LogisticRegression(max_iter=1000, random_state=42)
    
    print("4. Ejecutando Validación Cruzada K-Fold (cv=5)...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
    print(f"   -> Scores AUC en cada Fold: {cv_scores.round(4)}")
    print(f"   -> ROC-AUC Promedio (Train CV): {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    print("\n5. Entrenando el modelo final con todo el Train Set...")
    model.fit(X_train, y_train)
    
    print("6. Evaluando en el Test Set y Calculando ROC-AUC final...")
    # Predecir probabilidades (columna 1 = la probabilidad de que is_goal == 1)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"\n>>>> ROC-AUC DEFINITIVO OBTENIDO EN PRUEBAS: {auc_score:.4f} <<<<\n")
    
    # 7. Graficando Curva ROC
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='crimson', lw=2, label=f'Regresión Logística (AUC = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Azar (AUC = 0.500)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Tasa de Falsos Positivos (FPR)')
    plt.ylabel('Tasa de Verdaderos Positivos (TPR)')
    plt.title('Curva ROC - Predicción de Expected Goals (xG)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    
    # Crear directorio img si no existe y guardar
    os.makedirs(os.path.dirname(out_path_img), exist_ok=True)
    plt.savefig(out_path_img, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Éxito: La curva ROC se ha guardado físicamente en '{out_path_img}'.")
    return model

if __name__ == "__main__":
    train_xg_model()
