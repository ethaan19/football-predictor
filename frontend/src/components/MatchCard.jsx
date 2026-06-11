import TeamCrest from "./TeamCrest";

export default function MatchCard({ homeTeam, awayTeam, prediction }) {
  return (
    <div className="match-card">
      <div className="mc-team home">
        <div className="mc-crest-wrap">
          <TeamCrest name={homeTeam?.name} size={64} />
        </div>
        <div className="mc-name">{homeTeam?.name}</div>
        <div className="mc-role">Local</div>
      </div>

      <div className="mc-center">
        {prediction ? (
          <div className="mc-score">
            <span className="score-num">{prediction.predicted_home_goals ?? 0}</span>
            <span className="score-divider">-</span>
            <span className="score-num">{prediction.predicted_away_goals ?? 0}</span>
          </div>
        ) : (
          <div className="mc-vs">VS</div>
        )}
        <div className="mc-date">Predicción</div>
      </div>

      <div className="mc-team away">
        <div className="mc-crest-wrap">
          <TeamCrest name={awayTeam?.name} size={64} />
        </div>
        <div className="mc-name">{awayTeam?.name}</div>
        <div className="mc-role">Visitante</div>
      </div>
    </div>
  );
}
