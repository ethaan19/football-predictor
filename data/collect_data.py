"""
collect_data.py
---------------
Descarga partidos históricos de football-data.org (API gratuita).
Guarda los datos en data/matches_raw.csv para el entrenamiento.

Leagues descargadas (gratuitas con el plan Free):
  - PL   → Premier League (Inglaterra)
  - PD   → La Liga (España)
  - BL1  → Bundesliga (Alemania)
  - SA   → Serie A (Italia)
  - FL1  → Ligue 1 (Francia)

Uso:
    python data/collect_data.py
"""

import os
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

LEAGUES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
}

SEASONS = [2024, 2025]
OUTPUT_DIR = Path(__file__).parent / "raw"
OUTPUT_FILE = Path(__file__).parent / "matches_raw.csv"


def fetch_matches(league_code: str, season: int) -> list[dict]:
    """Descarga todos los partidos de una liga y temporada."""
    url = f"{BASE_URL}/competitions/{league_code}/matches"
    params = {"season": season, "status": "FINISHED"}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("matches", [])
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠️  Error {e.response.status_code} en {league_code}/{season}: {e}")
        return []
    except Exception as e:
        print(f"  ⚠️  Error inesperado en {league_code}/{season}: {e}")
        return []


def parse_match(match: dict, league: str) -> dict | None:
    """Extrae los campos relevantes de un objeto partido."""
    score = match.get("score", {})
    full_time = score.get("fullTime", {})
    home_goals = full_time.get("home")
    away_goals = full_time.get("away")

    if home_goals is None or away_goals is None:
        return None

    winner = score.get("winner")
    if winner == "HOME_TEAM":
        result = "H"
    elif winner == "AWAY_TEAM":
        result = "A"
    else:
        result = "D"

    return {
        "match_id":    match.get("id"),
        "date":        match.get("utcDate", "")[:10],
        "league":      league,
        "season":      match.get("season", {}).get("startYear"),
        "home_team":   match.get("homeTeam", {}).get("name"),
        "away_team":   match.get("awayTeam", {}).get("name"),
        "home_goals":  home_goals,
        "away_goals":  away_goals,
        "result":      result,          # H / D / A
    }


def main():
    print("⚽  Iniciando descarga de datos históricos...\n")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_matches = []

    for code, name in LEAGUES.items():
        for season in SEASONS:
            print(f"  📥  {name} — temporada {season}/{season+1}", end=" ... ")
            matches = fetch_matches(code, season)
            parsed = [r for m in matches if (r := parse_match(m, name)) is not None]
            all_matches.extend(parsed)
            print(f"{len(parsed)} partidos")
            time.sleep(6)   # Respeta el rate limit del plan gratuito (10 req/min)

    df = pd.DataFrame(all_matches)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅  Total: {len(df):,} partidos guardados en {OUTPUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
