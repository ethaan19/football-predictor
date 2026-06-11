import laligaLogo from "../assets/leagues/laliga.png";
import premierleagueLogo from "../assets/leagues/premierleague.png";
import bundesligaLogo from "../assets/leagues/bundesliga.png";
import serieaLogo from "../assets/leagues/seriea.png";
import ligue1Logo from "../assets/leagues/ligue1.png";

const LEAGUES = [
  { id: "La Liga",        logo: laligaLogo,        color: "#e34234" },
  { id: "Premier League", logo: premierleagueLogo, color: "#3b82f6" },
  { id: "Bundesliga",     logo: bundesligaLogo,     color: "#f59e0b" },
  { id: "Serie A",        logo: serieaLogo,        color: "#22c55e" },
  { id: "Ligue 1",        logo: ligue1Logo,        color: "#a855f7" },
];

export default function LeagueFilter({ selected, onChange }) {
  return (
    <div className="league-filter">
      <button
        className={`league-btn ${!selected ? "active" : ""}`}
        onClick={() => onChange(null)}
        title="Todas las ligas"
      >
        <div className="league-logo-wrapper">
          <span className="league-icon">🌐</span>
        </div>
      </button>
      {LEAGUES.map(({ id, logo, color }) => (
        <button
          key={id}
          className={`league-btn ${selected === id ? "active" : ""}`}
          style={
            selected === id
              ? { background: color, borderColor: color, color: "#fff" }
              : {}
          }
          onClick={() => onChange(id)}
          title={id}
        >
          <div className="league-logo-wrapper">
            <img 
              src={logo} 
              alt={id} 
              className={`league-logo-img ${id.toLowerCase().replace(/\s+/g, "")}`} 
            />
          </div>
        </button>
      ))}
    </div>
  );
}
