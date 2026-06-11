import TeamCrest from "./TeamCrest";

export default function LoadingOverlay({ homeTeam, awayTeam }) {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="loading-teams">
          <div className="loading-team">
            <TeamCrest name={homeTeam?.name} size={60} />
            <span className="loading-team-name">{homeTeam?.name}</span>
          </div>

          <div className="loading-middle">
            <span className="loading-ball">⚽</span>
            <span className="loading-vs">VS</span>
          </div>

          <div className="loading-team">
            <TeamCrest name={awayTeam?.name} size={60} />
            <span className="loading-team-name">{awayTeam?.name}</span>
          </div>
        </div>

        <div className="loading-progress">
          <div className="loading-status">
            ANALIZANDO
            <span className="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div className="loading-track">
            <div className="loading-bar" />
          </div>
          <div className="loading-detail">Procesando con Azure AI Foundry</div>
        </div>
      </div>
    </div>
  );
}
