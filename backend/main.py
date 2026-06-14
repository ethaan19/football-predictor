"""
main.py
-------
API REST con FastAPI para el Football Match Predictor.

Endpoints:
  GET  /               → Health check
  GET  /api/teams      → Lista de equipos disponibles
  POST /api/predict    → Predicción de resultado de partido

Uso:
    uvicorn backend.main:app --reload --port 8000
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from predictor import predict
from team_data import TEAMS_CATALOG, get_team_features

load_dotenv("../.env")

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Football Match Predictor API",
    description="Predicción de partidos de fútbol con XGBoost desplegado en Azure AI Foundry",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "https://football-predictor.vercel.app",  # Tu URL de Vercel
        "https://football-predictor-production-9561.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ─── Schemas ──────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    home_team: str
    away_team: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "home_team": "Real Madrid",
                "away_team": "FC Barcelona",
            }
        }
    }


class PredictionResult(BaseModel):
    home_team: str
    away_team: str
    home_win: float
    draw: float
    away_win: float
    predicted_home_goals: int
    predicted_away_goals: int
    confidence: str
    model_version: str


# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Football Match Predictor API"}


@app.get("/api/teams", tags=["Teams"])
def get_teams():
    return {
        "teams": [
            {"name": t["name"], "league": t["league"]}
            for t in TEAMS_CATALOG.values()
        ],
        "total": len(TEAMS_CATALOG),
    }


@app.post("/api/predict", response_model=PredictionResult, tags=["Prediction"])
async def predict_match(request: PredictRequest):
    """
    Predice el resultado de un partido entre dos equipos.
    Devuelve las probabilidades de victoria local, empate y victoria visitante.
    """
    if request.home_team == request.away_team:
        raise HTTPException(
            status_code=400,
            detail="El equipo local y visitante no pueden ser el mismo."
        )

    home_data = TEAMS_CATALOG.get(request.home_team)
    away_data  = TEAMS_CATALOG.get(request.away_team)

    if not home_data:
        raise HTTPException(status_code=404, detail=f"Equipo no encontrado: {request.home_team}")
    if not away_data:
        raise HTTPException(status_code=404, detail=f"Equipo no encontrado: {request.away_team}")

    # Construir features para el modelo
    features = get_team_features(home_data, away_data)

    # Llamar al endpoint de Azure ML
    prediction = await predict(home_data, away_data)

    # Calcular confianza basada en la probabilidad máxima
    max_prob = max(prediction["home_win"], prediction["draw"], prediction["away_win"])
    if max_prob >= 0.55:
        confidence = "ALTA"
    elif max_prob >= 0.40:
        confidence = "MEDIA"
    else:
        confidence = "BAJA"

    return PredictionResult(
        home_team=request.home_team,
        away_team=request.away_team,
        home_win=prediction["home_win"],
        draw=prediction["draw"],
        away_win=prediction["away_win"],
        predicted_home_goals=prediction.get("predicted_home_goals", 0),
        predicted_away_goals=prediction.get("predicted_away_goals", 0),
        confidence=confidence,
        model_version="gpt-4o-mini",
    )
