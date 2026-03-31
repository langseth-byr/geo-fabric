import { useEffect, useState } from "react";

interface HealthStatus {
  status: string;
  postgis: string | null;
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "unreachable", postgis: null }));
  }, []);

  return (
    <div style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>GeoFabric</h1>
      <p>
        API status:{" "}
        {health ? (
          <span>
            {health.status}
            {health.postgis ? ` (PostGIS ${health.postgis})` : ""}
          </span>
        ) : (
          "checking..."
        )}
      </p>
    </div>
  );
}

export default App;
