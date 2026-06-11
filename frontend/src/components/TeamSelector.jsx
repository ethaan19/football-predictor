import { useState, useEffect, useRef } from "react";
import TeamCrest from "./TeamCrest";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function TeamSelector({ label, side, value, onChange, excludeTeam, leagueFilter }) {
  const [teams, setTeams]   = useState([]);
  const [search, setSearch] = useState("");
  const [open, setOpen]     = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/teams`)
      .then(r => r.json())
      .then(data => setTeams(data.teams || []))
      .catch(() => setTeams([]));
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const filtered = teams.filter(t =>
    t.name !== excludeTeam &&
    (!leagueFilter || t.league === leagueFilter) &&
    t.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (team) => {
    onChange(team);
    setSearch("");
    setOpen(false);
  };

  return (
    <div className={`team-selector ${side}`} ref={ref}>
      <div className="crest-preview-slot">
        {value ? (
          <div className="crest-preview-active">
            <TeamCrest name={value.name} size={90} />
          </div>
        ) : (
          <div className="crest-preview-placeholder">
            {side === "home" ? (
              <svg className="placeholder-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
            ) : (
              <svg className="placeholder-icon away-plane" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21.5 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10.5 2.67 10.5 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L14.5 19v-5.5z" />
              </svg>
            )}
          </div>
        )}
      </div>

      <label className="selector-label">{label}</label>

      <button
        className={`selector-btn ${value ? "has-value" : ""}`}
        onClick={() => setOpen(o => !o)}
      >
        {value ? (
          <div className="selector-team-display">
            <span className="selector-team-name">{value.name}</span>
          </div>
        ) : (
          <span className="placeholder">Elige un equipo…</span>
        )}
        <span className="chevron">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="dropdown">
          <input
            className="search-input"
            placeholder="Buscar equipo..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            autoFocus
          />
          <ul className="team-list">
            {filtered.length === 0 && (
              <li className="no-results">Sin resultados</li>
            )}
            {filtered.map(team => (
              <li
                key={team.name}
                className="team-item"
                onClick={() => handleSelect(team)}
              >
                <TeamCrest name={team.name} size={24} />
                {team.name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
