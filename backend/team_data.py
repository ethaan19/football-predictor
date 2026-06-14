import json
from pathlib import Path

POSSIBLE_PATHS = [
    Path(__file__).parent.parent / "data" / "teams.json",
    Path("/app/data/teams.json"),
    Path("./data/teams.json"),
]

TEAMS_JSON = None
for path in POSSIBLE_PATHS:
    if path.exists():
        TEAMS_JSON = path
        break

_FALLBACK_CATALOG = {
    "Real Madrid CF": {
        "name": "Real Madrid CF", "league": "La Liga",
        "elo": 1708, "form_pts": 2.2, "form_gd": 1.0,
        "goals_avg": 2.3, "conceded_avg": 0.9,
    },
    "FC Barcelona": {
        "name": "FC Barcelona", "league": "La Liga",
        "elo": 1762, "form_pts": 2.3, "form_gd": 1.2,
        "goals_avg": 2.5, "conceded_avg": 0.8,
    },
}


def load_teams() -> dict:
    if TEAMS_JSON and TEAMS_JSON.exists():
        with open(TEAMS_JSON, encoding="utf-8") as f:
            return json.load(f)
    print("⚠️  teams.json no encontrado, usando catálogo básico.")
    return _FALLBACK_CATALOG

TEAMS_CATALOG = load_teams()

def get_team_features(home: dict, away: dict) -> dict:
    """Construye el vector de características para el modelo."""
    elo_home = home.get("elo", 1500)
    elo_away = away.get("elo", 1500)

    return {
        "home_elo":          elo_home,
        "away_elo":          elo_away,
        "elo_diff":          elo_home - elo_away,
        "home_form_pts":     home.get("form_pts", 1.0),
        "away_form_pts":     away.get("form_pts", 1.0),
        "home_form_gd":      home.get("form_gd", 0.0),
        "away_form_gd":      away.get("form_gd", 0.0),
        "home_goals_avg":    home.get("goals_avg", 1.2),
        "away_goals_avg":    away.get("goals_avg", 1.2),
        "home_conceded_avg": home.get("conceded_avg", 1.2),
        "away_conceded_avg": away.get("conceded_avg", 1.2),
        "h2h_home_wins":     0.33,
        "h2h_draws":         0.27,
        "h2h_away_wins":     0.40,
        "home_advantage":    1,
    }