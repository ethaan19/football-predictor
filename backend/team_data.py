import json
from pathlib import Path

TEAMS_JSON = Path(__file__).parent.parent / "data" / "teams.json"

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
    if TEAMS_JSON.exists():
        with open(TEAMS_JSON, encoding="utf-8") as f:
            return json.load(f)
    print("⚠️  teams.json no encontrado, usando catálogo básico.")
    return _FALLBACK_CATALOG


TEAMS_CATALOG = load_teams()


def get_team_features(home: dict, away: dict) -> dict:
    elo_home = home["elo"]
    elo_away = away["elo"]
    return {
        "home_elo":          elo_home,
        "away_elo":          elo_away,
        "elo_diff":          elo_home - elo_away,
        "home_form_pts":     home["form_pts"],
        "away_form_pts":     away["form_pts"],
        "home_form_gd":      home["form_gd"],
        "away_form_gd":      away["form_gd"],
        "home_goals_avg":    home["goals_avg"],
        "away_goals_avg":    away["goals_avg"],
        "home_conceded_avg": home["conceded_avg"],
        "away_conceded_avg": away["conceded_avg"],
        "h2h_home_wins":     0.33,
        "h2h_draws":         0.27,
        "h2h_away_wins":     0.40,
        "home_advantage":    1,
    }