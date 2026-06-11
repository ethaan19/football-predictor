import { useState } from "react";
import { getTeamCrest } from "../teamCrests";

export default function TeamCrest({ name, size = 40 }) {
  const [error, setError] = useState(false);
  const url = getTeamCrest(name);

  const initials = name
    ? name.split(" ").filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join("")
    : "?";

  const fontSize = Math.max(9, Math.round(size * 0.32));

  if (!url || error) {
    return (
      <div
        className="crest-fallback"
        style={{ width: size, height: size, fontSize }}
      >
        {initials}
      </div>
    );
  }

  return (
    <img
      className="crest-img"
      src={url}
      alt={name}
      width={size}
      height={size}
      onError={() => setError(true)}
      style={{ width: size, height: size }}
    />
  );
}
