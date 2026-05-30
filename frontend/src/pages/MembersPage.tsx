import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import * as api from "../lib/api";
import type { Member } from "../lib/types";

export function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentOnly, setCurrentOnly] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.listMembers({ limit: 100, current_only: currentOnly });
        setMembers(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load members");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [currentOnly]);

  return (
    <>
      <div className="page-header">
        <div>
          <h2>Members of Parliament</h2>
          <p>Commons MPs with party and constituency terms from the Members API.</p>
        </div>
      </div>

      <div className="toolbar">
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <input
            type="checkbox"
            checked={currentOnly}
            onChange={(event) => setCurrentOnly(event.target.checked)}
          />
          Current MPs only
        </label>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading members…</div>
      ) : (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Display name</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id}>
                  <td>{member.name}</td>
                  <td>{member.display_name ?? "—"}</td>
                  <td>
                    {member.is_current ? (
                      <span className="badge success">Current</span>
                    ) : (
                      <span className="badge">Former</span>
                    )}
                  </td>
                  <td>
                    <Link to={`/members/${member.id}`}>View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
