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
You are an expert football analyst. Analyze this match and return ONLY a JSON.

HOME Team: {home['name']}
- ELO: {home['elo']} | Form (pts/match): {home['form_pts']} | Goal Diff: {home['form_gd']}
- Avg Goals Scored: {home['goals_avg']} | Conceded: {home['conceded_avg']}

AWAY Team: {away['name']}
- ELO: {away['elo']} | Form (pts/match): {away['form_pts']} | Goal Diff: {away['form_gd']}
- Avg Goals Scored: {away['goals_avg']} | Conceded: {away['conceded_avg']}

Be realistic and precise when predicting:
- If there is a significant difference in ELO, form, and squad strength between the teams (for example, an elite team like Real Madrid CF or FC Barcelona against a team of much lower ELO/level), the goal prediction should reflect that superiority realistically (e.g., scores like 3-0, 3-1, 4-0, or 4-1 instead of a generic and conservative 2-1).
- Avoid predicting excessive or unrealistic thrashings (like 7-0 or 8-1) unless the difference in goals scored/conceded statistics and ELO is truly abysmal and extreme.
- If the teams are evenly matched, be moderate with goals (e.g., 1-0, 1-1, 1-2, 2-1).

Return ONLY this JSON (no markdown, no extra text):
{{"home_win": 0.XX, "draw": 0.XX, "away_win": 0.XX, "predicted_home_goals": X, "predicted_away_goals": Y}}
Where "home_win", "draw", and "away_win" are decimal probabilities that must sum exactly 1.0, and "predicted_home_goals" and "predicted_away_goals" are the prediction of the most likely integer number of goals for each team.
"""

    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100,
    )

    return json.loads(response.choices[0].message.content)