import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix, classification_report, ConfusionMatrixDisplay

def train_xg_model():
    print("=====================================================")
    print(" Entrenando Modelo de Expected Goals (xG) - Logística")
    print("=====================================================\n")
    
    # 1. Resolución segura de la ruta del dataset (Doble nivel de retroceso por nueva arquitectura)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', '..', 'data', 'xg_train.csv')
    out_path_img = os.path.join(current_dir, '..', '..', 'img', 'roc_curve_xg.png')

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Error Crítico: No se encontró el archivo en la ruta absoluta calculada:\\n{data_path}")

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
    
    print("3. Configurando modelo de Regresión Logística (Penalizando Desbalanceo)...")
    # Utilizamos class_weight='balanced' para castigar doblemente fallar los Goles
    model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    
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
    
    os.makedirs(os.path.dirname(out_path_img), exist_ok=True)
    plt.savefig(out_path_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Éxito: La curva ROC se ha guardado físicamente en '{out_path_img}'.")

    # --- REPORTE DE CLASIFICACIÓN OFICIAL ---
    y_pred = model.predict(X_test)
    print("\\n-============= REPORTE DE CLASIFICACIÓN =============-")
    print(classification_report(y_test, y_pred, target_names=['Fallos (0)', 'Goles (1)']))
    print("-====================================================-")

    # --- MATRIZ DE CONFUSIÓN ---
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Gol Fallado', 'GOL Anotado'])
    
    fig, ax = plt.subplots(figsize=(6, 6))
    disp.plot(cmap='Blues', ax=ax, values_format='d')
    plt.title('Matriz de Confusión - Penalty Class Balaceado', fontsize=14, fontweight='bold')
    
    out_path_cm = out_path_img.replace('roc_curve_xg.png', 'confusion_matrix_xg.png')
    plt.savefig(out_path_cm, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Éxito: Matriz de Confusión se ha guardado físicamente en '{out_path_cm}'.")
    return model

if __name__ == "__main__":
    train_xg_model()
