import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import * as api from "../lib/api";

export function HomePage() {
  const [stats, setStats] = useState({
    parties: 0,
    elections: 0,
    members: 0,
    manifestos: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [parties, elections, members, manifestos] = await Promise.all([
          api.listParties(1, 0),
          api.listElections(1, 0),
          api.listMembers({ limit: 1, current_only: true }),
          api.listManifestos({ limit: 1, offset: 0 }),
        ]);
        setStats({
          parties: parties.count,
          elections: elections.count,
          members: members.count,
          manifestos: manifestos.count,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load overview");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  return (
    <>
      <div className="page-header">
        <div>
          <h2>Overview</h2>
          <p>Browse collected UK election results, MPs, parties, and manifestos.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading overview…</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <span>Parties</span>
              <strong>{stats.parties}</strong>
            </div>
            <div className="stat-card">
              <span>Elections</span>
              <strong>{stats.elections}</strong>
            </div>
            <div className="stat-card">
              <span>Current MPs</span>
              <strong>{stats.members}</strong>
            </div>
            <div className="stat-card">
              <span>Manifestos</span>
              <strong>{stats.manifestos}</strong>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h3 style={{ marginTop: 0, color: "var(--blue-900)" }}>Explore the data</h3>
              <p style={{ color: "var(--slate-500)" }}>
                Use the sidebar to inspect general elections since 2010, current Commons members,
                constituency records, and party manifesto texts.
              </p>
              <div className="toolbar">
                <Link className="btn btn-primary" to="/elections">
                  View elections
                </Link>
                <Link className="btn btn-secondary" to="/members">
                  Browse MPs
                </Link>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
