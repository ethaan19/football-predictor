"""
score.py
--------
Script de inferencia para el Azure ML Managed Online Endpoint.
Azure ML llama a init() al arrancar el contenedor y a run() en cada petición.

Este fichero se despliega junto con el modelo en Azure AI Foundry.
"""

import os
import json
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)
model = None

FEATURE_COLS = [
    "home_elo", "away_elo", "elo_diff",
    "home_form_pts", "away_form_pts",
    "home_form_gd", "away_form_gd",
    "home_goals_avg", "away_goals_avg",
    "home_conceded_avg", "away_conceded_avg",
    "h2h_home_wins", "h2h_draws", "h2h_away_wins",
    "home_advantage",
]


def init():
    """Carga el modelo cuando el endpoint arranca. Azure ML lo llama una vez."""
    global model

    # Azure ML inyecta la ruta al directorio del modelo aquí
    model_dir = os.environ.get("AZUREML_MODEL_DIR", ".")
    model_path = os.path.join(model_dir, "artifacts", "xgboost_model.pkl")

    logger.info(f"Cargando modelo desde {model_path}")
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    logger.info("Modelo cargado correctamente.")


def run(raw_data: str) -> str:
    """
    Realiza la predicción.

    Entrada (JSON string):
    {
        "features": {
            "home_elo": 1620,
            "away_elo": 1580,
            ...
        }
    }

    Salida (JSON string):
    {
        "home_win": 0.48,
        "draw": 0.24,
        "away_win": 0.28
    }
    """
    try:
        data = json.loads(raw_data)
        features = data["features"]

        # Construir vector de features en el orden correcto
        X = np.array([[features.get(col, 0.0) for col in FEATURE_COLS]])

        # Predecir probabilidades
        proba = model.predict_proba(X)[0]

        result = {
            "home_win":  round(float(proba[0]), 4),
            "draw":      round(float(proba[1]), 4),
            "away_win":  round(float(proba[2]), 4),
        }

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error en inferencia: {e}")
        return json.dumps({"error": str(e)})
