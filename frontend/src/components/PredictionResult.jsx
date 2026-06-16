import { useEffect, useState } from "react";

const CONFIDENCE_STYLES = {
  HIGH:  { color: "#34d399", bg: "rgba(52,211,153,0.08)",  border: "rgba(52,211,153,0.3)" },
  MEDIUM: { color: "#fbbf24", bg: "rgba(251,191,36,0.08)",  border: "rgba(251,191,36,0.3)" },
  LOW:  { color: "#f43f5e", bg: "rgba(244,63,94,0.08)",   border: "rgba(244,63,94,0.3)" },
};

const OUTCOMES_META = {
  home: { dot: "#38bdf8", barClass: "home" },
  draw: { dot: "#94a3b8", barClass: "draw" },
  away: { dot: "#f43f5e", barClass: "away" },
};

export default function PredictionResult({ prediction }) {
  const { home_team, away_team, home_win, draw, away_win, confidence } = prediction;

  const outcomes = [
    { key: "home", label: `${home_team} Win (Home)`, value: home_win },
    { key: "draw", label: "Draw",                 value: draw     },
    { key: "away", label: `${away_team} Win (Away)`,  value: away_win },
  ];

  const best = outcomes.reduce((a, b) => (a.value > b.value ? a : b));
  const confStyle = CONFIDENCE_STYLES[confidence] ?? CONFIDENCE_STYLES.MEDIUM;
  const winnerColor = OUTCOMES_META[best.key].dot;

  const [animated, setAnimated] = useState(false);
  useEffect(() => {
    const id = setTimeout(() => setAnimated(true), 60);
    return () => clearTimeout(id);
  }, []);

  return (
    <div className="prediction-result">
      <div
        className="winner-banner"
        style={{
          background: `linear-gradient(135deg, var(--surface) 0%, ${winnerColor}0d 100%)`,
        }}
      >
        <span className="winner-icon">🏆</span>
        <div className="winner-info">
          <div className="winner-label">Most likely outcome</div>
          <div className="winner-name" style={{ color: winnerColor }}>{best.label}</div>
        </div>
        <div className="winner-right">
          <span className="winner-pct" style={{ color: winnerColor }}>
            {(best.value * 100).toFixed(1)}%
          </span>
          <span
            className="confidence-chip"
            style={{ color: confStyle.color, background: confStyle.bg, borderColor: confStyle.border }}
          >
            Confidence: {confidence}
          </span>
        </div>
      </div>

      <div className="prob-bars">
        {outcomes.map(({ key, label, value }) => {
          const { dot, barClass } = OUTCOMES_META[key];
          const pct = value * 100;
          return (
            <div key={key} className="prob-bar-item">
              <div className="prob-bar-header">
                <span className="prob-bar-label">
                  <span className="prob-bar-dot" style={{ background: dot }} />
                  {label}
                </span>
                <span className="prob-bar-pct" style={{ color: dot }}>
                  {pct.toFixed(1)}%
                </span>
              </div>
              <div className="prob-track">
                <div
                  className={`prob-fill ${barClass}`}
                  style={{ width: animated ? `${pct}%` : "0%" }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
