"""
features.py
-----------
Ingeniería de características para el modelo de predicción de fútbol.

Calcula para cada partido:
  - Rating ELO dinámico (actualizado partido a partido)
  - Forma reciente (últimos N partidos)
  - Estadísticas ofensivas/defensivas recientes
  - Historial head-to-head

Uso:
    from model.features import FeatureEngineer
    fe = FeatureEngineer()
    df_features = fe.build_features(df_matches)
"""

import numpy as np
import pandas as pd
from collections import defaultdict


# ─── Configuración ELO ──────────────────────────────────────────────────────
ELO_START     = 1500   # Rating inicial de todos los equipos
ELO_K         = 32     # Factor K (sensibilidad del ELO)
ELO_HOME_ADV  = 100    # Ventaja de local en ELO

# ─── Ventana de forma reciente ───────────────────────────────────────────────
FORM_WINDOW   = 5      # Últimos N partidos para calcular la forma
STATS_WINDOW  = 10     # Últimos N partidos para estadísticas de goles
H2H_WINDOW    = 10     # Últimos N enfrentamientos directos


class EloCalculator:
    """Calcula ratings ELO dinámicos para todos los equipos."""

    def __init__(self, k: float = ELO_K, home_adv: float = ELO_HOME_ADV):
        self.k = k
        self.home_adv = home_adv
        self.ratings: dict[str, float] = defaultdict(lambda: ELO_START)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update(self, home_team: str, away_team: str, result: str) -> tuple[float, float]:
        """
        Actualiza los ratings ELO y devuelve los ratings ANTES del partido
        (para usar como features sin data leakage).
        """
        r_home = self.ratings[home_team]
        r_away = self.ratings[away_team]

        # Ratings antes del partido (los que se usan como feature)
        pre_home = r_home
        pre_away = r_away

        # Resultado real: 1=victoria local, 0.5=empate, 0=victoria visitante
        actual = {"H": 1.0, "D": 0.5, "A": 0.0}[result]

        # Resultado esperado (con ventaja de local)
        exp_home = self.expected_score(r_home + self.home_adv, r_away)
        exp_away = 1 - exp_home

        # Actualizar ratings
        self.ratings[home_team] = r_home + self.k * (actual - exp_home)
        self.ratings[away_team] = r_away + self.k * ((1 - actual) - exp_away)

        return pre_home, pre_away


class FeatureEngineer:
    """Construye el DataFrame de features a partir de los partidos históricos."""

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Entrada: DataFrame con columnas
            [match_id, date, league, season, home_team, away_team,
             home_goals, away_goals, result]

        Salida: DataFrame con features ML listo para entrenamiento.
        """
        df = df.copy().sort_values("date").reset_index(drop=True)

        elo_calc = EloCalculator()
        team_history: dict[str, list[dict]] = defaultdict(list)
        h2h_history: dict[tuple, list[dict]] = defaultdict(list)

        rows = []

        for _, match in df.iterrows():
            home = match["home_team"]
            away = match["away_team"]
            result = match["result"]

            # ── ELO antes del partido ────────────────────────────────────────
            elo_home, elo_away = elo_calc.update(home, away, result)

            # ── Forma reciente ───────────────────────────────────────────────
            home_form = self._get_form(team_history[home], FORM_WINDOW)
            away_form = self._get_form(team_history[away], FORM_WINDOW)

            # ── Estadísticas de goles ────────────────────────────────────────
            home_stats = self._get_goal_stats(team_history[home], STATS_WINDOW)
            away_stats = self._get_goal_stats(team_history[away], STATS_WINDOW)

            # ── Head-to-head ─────────────────────────────────────────────────
            h2h_key = tuple(sorted([home, away]))
            h2h = self._get_h2h(h2h_history[h2h_key], home, H2H_WINDOW)

            row = {
                # Identificadores (no se usan como features)
                "match_id":   match["match_id"],
                "date":       match["date"],
                "home_team":  home,
                "away_team":  away,

                # Features
                "home_elo":               elo_home,
                "away_elo":               elo_away,
                "elo_diff":               elo_home - elo_away,
                "home_form_pts":          home_form["pts"],
                "away_form_pts":          away_form["pts"],
                "home_form_gd":           home_form["gd"],
                "away_form_gd":           away_form["gd"],
                "home_goals_avg":         home_stats["goals_scored"],
                "away_goals_avg":         away_stats["goals_scored"],
                "home_conceded_avg":      home_stats["goals_conceded"],
                "away_conceded_avg":      away_stats["goals_conceded"],
                "h2h_home_wins":          h2h["home_wins"],
                "h2h_draws":              h2h["draws"],
                "h2h_away_wins":          h2h["away_wins"],
                "home_advantage":         1,

                # Target
                "result":     {"H": 0, "D": 1, "A": 2}[result],
            }
            rows.append(row)

            # Actualizar historial con el resultado de este partido
            home_record = {
                "goals_scored": match["home_goals"],
                "goals_conceded": match["away_goals"],
                "pts": self._result_to_pts(result, "H"),
                "gd": match["home_goals"] - match["away_goals"],
            }
            away_record = {
                "goals_scored": match["away_goals"],
                "goals_conceded": match["home_goals"],
                "pts": self._result_to_pts(result, "A"),
                "gd": match["away_goals"] - match["home_goals"],
            }
            team_history[home].append(home_record)
            team_history[away].append(away_record)

            h2h_history[h2h_key].append({
                "home": home,
                "result": result,
            })

        return pd.DataFrame(rows)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _result_to_pts(result: str, side: str) -> int:
        if result == "H":
            return 3 if side == "H" else 0
        elif result == "A":
            return 0 if side == "H" else 3
        return 1  # Empate

    @staticmethod
    def _get_form(history: list[dict], window: int) -> dict:
        recent = history[-window:] if len(history) >= window else history
        if not recent:
            return {"pts": 1.5, "gd": 0.0}  # Valor neutral si no hay historial
        return {
            "pts": np.mean([r["pts"] for r in recent]),
            "gd":  np.mean([r["gd"] for r in recent]),
        }

    @staticmethod
    def _get_goal_stats(history: list[dict], window: int) -> dict:
        recent = history[-window:] if len(history) >= window else history
        if not recent:
            return {"goals_scored": 1.3, "goals_conceded": 1.3}
        return {
            "goals_scored":   np.mean([r["goals_scored"] for r in recent]),
            "goals_conceded": np.mean([r["goals_conceded"] for r in recent]),
        }

    @staticmethod
    def _get_h2h(history: list[dict], home_team: str, window: int) -> dict:
        recent = history[-window:] if len(history) >= window else history
        if not recent:
            return {"home_wins": 0.33, "draws": 0.27, "away_wins": 0.40}

        home_wins = sum(1 for r in recent if r["home"] == home_team and r["result"] == "H")
        away_wins = sum(1 for r in recent if r["home"] == home_team and r["result"] == "A")
        draws     = sum(1 for r in recent if r["result"] == "D")
        total     = len(recent)

        return {
            "home_wins": home_wins / total,
            "draws":     draws / total,
            "away_wins": away_wins / total,
        }


FEATURE_COLS = [
    "home_elo", "away_elo", "elo_diff",
    "home_form_pts", "away_form_pts",
    "home_form_gd", "away_form_gd",
    "home_goals_avg", "away_goals_avg",
    "home_conceded_avg", "away_conceded_avg",
    "h2h_home_wins", "h2h_draws", "h2h_away_wins",
    "home_advantage",
]
