"""
generate_teams.py
-----------------
Reads data/matches_raw.csv and generates data/teams.json with the
real stats of each team (ELO, form, goals).

Usage:
    python data/generate_teams.py
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

DATA_DIR    = Path(__file__).parent
CSV_FILE    = DATA_DIR / "matches_raw.csv"
OUTPUT_FILE = DATA_DIR / "teams.json"

WINDOW    = 10   # Last N matches to compute stats
ELO_START = 1500
ELO_K     = 32
ELO_HOME  = 60


def expected(ra, rb):
    return 1 / (1 + 10 ** ((rb - ra) / 400))


def main():
    print("📊  Generating teams.json from matches_raw.csv...\n")

    df = pd.read_csv(CSV_FILE, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    print(f"  {len(df):,} matches loaded")

    # ── Dynamic ELO ──────────────────────────────────────────────────────────
    elo = defaultdict(lambda: ELO_START)
    for _, row in df.iterrows():
        h, a, r = row["home_team"], row["away_team"], row["result"]
        rh, ra = elo[h], elo[a]
        actual = 1.0 if r == "H" else (0.5 if r == "D" else 0.0)
        exp_h  = expected(rh + ELO_HOME, ra)
        elo[h] = rh + ELO_K * (actual - exp_h)
        elo[a] = ra + ELO_K * ((1 - actual) - (1 - exp_h))

    # ── Match history per team ───────────────────────────────────────────────────
    team_matches = defaultdict(list)
    league_map   = {}

    for _, row in df.iterrows():
        h, a   = row["home_team"], row["away_team"]
        hg, ag = row["home_goals"], row["away_goals"]
        r      = row["result"]

        league_map[h] = row["league"]
        league_map[a] = row["league"]

        team_matches[h].append({
            "scored":   hg,
            "conceded": ag,
            "pts":      3 if r == "H" else (1 if r == "D" else 0),
        })
        team_matches[a].append({
            "scored":   ag,
            "conceded": hg,
            "pts":      3 if r == "A" else (1 if r == "D" else 0),
        })

    # ── Compute stats ─────────────────────────────────────────────────────────
    teams = {}
    for team, matches in team_matches.items():
        recent = matches[-WINDOW:]
        teams[team] = {
            "name":          team,
            "league":        league_map.get(team, ""),
            "elo":           round(elo[team], 1),
            "form_pts":      round(float(np.mean([m["pts"]      for m in recent])), 2),
            "form_gd":       round(float(np.mean([m["scored"] - m["conceded"] for m in recent])), 2),
            "goals_avg":     round(float(np.mean([m["scored"]   for m in recent])), 2),
            "conceded_avg":  round(float(np.mean([m["conceded"] for m in recent])), 2),
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)

    print(f"  {len(teams)} teams generated\n")

    # Top 10 ELO
    top = sorted(teams.values(), key=lambda x: x["elo"], reverse=True)[:10]
    print("  Top 10 teams by ELO:")
    for t in top:
        print(f"    {t['elo']:>7.1f}  {t['name']}")

    print(f"\n✅  Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()