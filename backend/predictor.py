import json
import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv("../.env")

async def predict(home: dict, away: dict) -> dict:
    client = AsyncAzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
    )

    prompt = f"""
Eres un analista experto en fútbol. Analiza este partido y devuelve SOLO un JSON.

Equipo LOCAL: {home['name']}
- ELO: {home['elo']} | Forma (pts/partido): {home['form_pts']} | Dif. goles: {home['form_gd']}
- Media goles marcados: {home['goals_avg']} | encajados: {home['conceded_avg']}

Equipo VISITANTE: {away['name']}
- ELO: {away['elo']} | Forma (pts/partido): {away['form_pts']} | Dif. goles: {away['form_gd']}
- Media goles marcados: {away['goals_avg']} | encajados: {away['conceded_avg']}

Sé realista y preciso al predecir:
- Si hay una diferencia significativa de ELO, forma y nivel de plantilla entre los equipos (por ejemplo, un equipo de élite como el Real Madrid CF o FC Barcelona contra un equipo de ELO/nivel muy inferior), la predicción de goles debe reflejar esa superioridad con realismo (ej. marcadores como 3-0, 3-1, 4-0 o 4-1 en vez de un genérico y conservador 2-1).
- Evita predecir goleadas desmesuradas o irreales (como 7-0 o 8-1) a menos que la diferencia en estadísticas de goles marcados/recibidos y ELO sea verdaderamente abismal y extrema.
- Si los equipos están igualados, sé moderado con los goles (ej. 1-0, 1-1, 1-2, 2-1).

Devuelve ÚNICAMENTE este JSON (sin markdown, sin texto extra):
{{"home_win": 0.XX, "draw": 0.XX, "away_win": 0.XX, "predicted_home_goals": X, "predicted_away_goals": Y}}
Donde "home_win", "draw" y "away_win" son las probabilidades decimales que deben sumar exactamente 1.0, y "predicted_home_goals" y "predicted_away_goals" son la predicción del número entero de goles más probable para cada equipo.
"""

    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100,
    )

    return json.loads(response.choices[0].message.content)