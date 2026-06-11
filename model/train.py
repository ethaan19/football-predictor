"""
train.py
--------
Entrena el modelo XGBoost para predicción de partidos de fútbol.

Pipeline:
  1. Carga datos históricos (data/matches_raw.csv)
  2. Aplica feature engineering (ELO, forma, h2h)
  3. Entrena XGBoost con TimeSeriesSplit (sin data leakage temporal)
  4. Evalúa el modelo (accuracy, log-loss, report)
  5. Guarda el modelo en model/artifacts/

Uso:
    cd football-predictor
    python model/train.py
"""

import sys
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score,
    log_loss,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

# Añadir raíz al path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from model.features import FeatureEngineer, FEATURE_COLS

# ─── Rutas ──────────────────────────────────────────────────────────────────
DATA_FILE      = ROOT / "data" / "matches_raw.csv"
ARTIFACTS_DIR  = Path(__file__).parent / "artifacts"
MODEL_FILE     = ARTIFACTS_DIR / "xgboost_model.pkl"
METADATA_FILE  = ARTIFACTS_DIR / "model_metadata.json"


def load_and_prepare_data() -> tuple[pd.DataFrame, pd.Series]:
    print("📂  Cargando datos...")
    df_raw = pd.read_csv(DATA_FILE, parse_dates=["date"])
    print(f"    {len(df_raw):,} partidos cargados\n")

    print("⚙️   Construyendo features...")
    fe = FeatureEngineer()
    df_features = fe.build_features(df_raw)

    # Descartar los primeros 200 partidos (ELO aún no está calibrado)
    df_features = df_features.iloc[200:].reset_index(drop=True)

    X = df_features[FEATURE_COLS]
    y = df_features["result"]   # 0=local, 1=empate, 2=visitante

    print(f"    {len(X):,} ejemplos con {len(FEATURE_COLS)} features")
    print(f"    Distribución de resultados:")
    labels = {0: "Victoria local", 1: "Empate", 2: "Victoria visitante"}
    for k, v in y.value_counts().sort_index().items():
        print(f"      {labels[k]}: {v:,} ({v/len(y)*100:.1f}%)")
    print()

    return X, y, df_features


def train_model(X: pd.DataFrame, y: pd.Series) -> xgb.XGBClassifier:
    """Entrena con validación cruzada temporal."""
    print("🏋️   Entrenando modelo XGBoost...")

    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )

    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = []

    print("    Validación cruzada temporal (5 folds):")
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        preds = model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        cv_scores.append(acc)
        print(f"      Fold {fold}: accuracy = {acc:.4f}")

    print(f"\n    CV Accuracy media: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")

    # Entrenamiento final con todos los datos
    print("\n    Entrenamiento final con todos los datos...")
    model.fit(X, y, verbose=False)

    return model


def evaluate_model(model: xgb.XGBClassifier, X: pd.DataFrame, y: pd.Series) -> dict:
    """Evaluación completa del modelo."""
    print("\n📊  Evaluación del modelo (conjunto completo):")

    proba = model.predict_proba(X)
    preds = model.predict(X)

    acc     = accuracy_score(y, preds)
    logloss = log_loss(y, proba)

    print(f"    Accuracy : {acc:.4f}")
    print(f"    Log-Loss : {logloss:.4f}")
    print()
    print(classification_report(
        y, preds,
        target_names=["Victoria local", "Empate", "Victoria visitante"]
    ))

    # Importancia de features
    print("🔍  Importancia de features (top 10):")
    importance = pd.Series(
        model.feature_importances_,
        index=FEATURE_COLS
    ).sort_values(ascending=False)
    for feat, imp in importance.head(10).items():
        bar = "█" * int(imp * 200)
        print(f"    {feat:<28} {imp:.4f}  {bar}")

    return {
        "accuracy": float(acc),
        "log_loss": float(logloss),
        "n_samples": len(X),
        "feature_importance": importance.to_dict(),
    }


def save_artifacts(model: xgb.XGBClassifier, metadata: dict):
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)

    metadata["model_file"] = str(MODEL_FILE.name)
    metadata["feature_cols"] = FEATURE_COLS

    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n💾  Modelo guardado en {MODEL_FILE}")
    print(f"💾  Metadata guardada en {METADATA_FILE}")


def main():
    print("=" * 60)
    print("  FOOTBALL MATCH PREDICTOR — Entrenamiento del modelo")
    print("=" * 60)
    print()

    X, y, df_features = load_and_prepare_data()
    model = train_model(X, y)
    metadata = evaluate_model(model, X, y)
    save_artifacts(model, metadata)

    print("\n✅  Entrenamiento completado. Siguiente paso:")
    print("    python model/deploy_azure.py")


if __name__ == "__main__":
    main()
