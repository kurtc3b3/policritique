import { useEffect, useState } from "react";

import * as api from "../lib/api";
import type { Party } from "../lib/types";

export function PartiesPage() {
  const [parties, setParties] = useState<Party[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listParties(100, 0);
        setParties(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load parties");
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
          <h2>Parties</h2>
          <p>Political parties referenced in election and member data.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading parties…</div>
      ) : (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Short name</th>
                <th>EC ID</th>
              </tr>
            </thead>
            <tbody>
              {parties.map((party) => (
                <tr key={party.id}>
                  <td>{party.name}</td>
                  <td>{party.short_name ?? "—"}</td>
                  <td>{party.ec_id ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
