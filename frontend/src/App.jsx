import { useState, useCallback } from "react";
import TeamSelector from "./components/TeamSelector";
import PredictionResult from "./components/PredictionResult";
import MatchCard from "./components/MatchCard";
import LeagueFilter from "./components/LeagueFilter";
import LoadingOverlay from "./components/LoadingOverlay";
import logo from "./assets/logo.png";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [homeTeam, setHomeTeam] = useState(null);
  const [awayTeam, setAwayTeam] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLeagueChange = (league) => {
    setSelectedLeague(league);
    setHomeTeam(null);
    setAwayTeam(null);
    setPrediction(null);
  };

  const handlePredict = useCallback(async () => {
    if (!homeTeam || !awayTeam) return;
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          home_team: homeTeam.name,
          away_team: awayTeam.name,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Prediction error");
      }

      const data = await res.json();
      setPrediction(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [homeTeam, awayTeam]);

  const canPredict = homeTeam && awayTeam && homeTeam.name !== awayTeam.name;

  return (
    <div className="app">
      {loading && <LoadingOverlay homeTeam={homeTeam} awayTeam={awayTeam} />}

      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <img src={logo} className="logo-img" alt="Logo" />
            <h1>Football Predictor</h1>
          </div>
        </div>
      </header>

      <main className="main">
        <LeagueFilter selected={selectedLeague} onChange={handleLeagueChange} />

        <section className={`pitch-section ${prediction ? "has-prediction" : ""}`}>
          <div className="pitch-bg" aria-hidden="true">
            <div className="pitch-penalty-box left" />
            <div className="pitch-penalty-box right" />
            <div className="pitch-corner tl" />
            <div className="pitch-corner tr" />
            <div className="pitch-corner bl" />
            <div className="pitch-corner br" />
          </div>

          <div className="selectors">
            <TeamSelector
              label="Home Team"
              side="home"
              value={homeTeam}
              onChange={setHomeTeam}
              excludeTeam={awayTeam?.name}
              leagueFilter={selectedLeague}
            />

            <div className="vs-block">
              <span className="vs-text">VS</span>
              <button
                className={`predict-btn desktop-predict-btn ${loading ? "loading" : ""} ${canPredict ? "active" : ""}`}
                onClick={handlePredict}
                disabled={!canPredict || loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>Predict</>
                )}
              </button>
            </div>

            <TeamSelector
              label="Away Team"
              side="away"
              value={awayTeam}
              onChange={setAwayTeam}
              excludeTeam={homeTeam?.name}
              leagueFilter={selectedLeague}
            />
          </div>

          <button
            className={`predict-btn mobile-predict-btn ${loading ? "loading" : ""} ${canPredict ? "active" : ""}`}
            onClick={handlePredict}
            disabled={!canPredict || loading}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing...
              </>
            ) : (
              <>Predict</>
            )}
          </button>
        </section>

        {error && (
          <div className="error-box">❌ {error}</div>
        )}

        {prediction && (
          <section className="result-section">
            <MatchCard homeTeam={homeTeam} awayTeam={awayTeam} prediction={prediction} />
            <PredictionResult prediction={prediction} />
          </section>
        )}

        {!prediction && !loading && (
          <div className="hint">
            Select a league and two teams, then press <strong>Predict</strong>.
          </div>
        )}
      </main>

      <footer className="footer">
        <p className="disclaimer">
          Predictions are probabilistic and do not guarantee the actual outcome.
        </p>
      </footer>
    </div>
  );
}
