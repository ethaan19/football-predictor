"""
score.py
--------
Inference script for the Azure ML Managed Online Endpoint.
Azure ML calls init() when the container starts and run() on each request.

This file is deployed along with the model in Azure AI Foundry.
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
    """Loads the model when the endpoint starts. Azure ML calls it once."""
    global model

    # Azure ML injects the path to the model directory here
    model_dir = os.environ.get("AZUREML_MODEL_DIR", ".")
    model_path = os.path.join(model_dir, "artifacts", "xgboost_model.pkl")

    logger.info(f"Loading model from {model_path}")
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    logger.info("Model loaded successfully.")


def run(raw_data: str) -> str:
    """
    Performs the prediction.

    Input (JSON string):
    {
        "features": {
            "home_elo": 1620,
            "away_elo": 1580,
            ...
        }
    }

    Output (JSON string):
    {
        "home_win": 0.48,
        "draw": 0.24,
        "away_win": 0.28
    }
    """
    try:
        data = json.loads(raw_data)
        features = data["features"]

        # Build feature vector in the correct order
        X = np.array([[features.get(col, 0.0) for col in FEATURE_COLS]])

        # Predict probabilities
        proba = model.predict_proba(X)[0]

        result = {
            "home_win":  round(float(proba[0]), 4),
            "draw":      round(float(proba[1]), 4),
            "away_win":  round(float(proba[2]), 4),
        }

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return json.dumps({"error": str(e)})
