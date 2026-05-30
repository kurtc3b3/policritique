import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import * as api from "../lib/api";
import type { Manifesto } from "../lib/types";

export function ManifestosPage() {
  const [manifestos, setManifestos] = useState<Manifesto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listManifestos({ limit: 50, offset: 0 });
        setManifestos(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load manifestos");
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
          <h2>Manifestos</h2>
          <p>Party policy documents collected from Manifesto Project and official PDFs.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading manifestos…</div>
      ) : manifestos.length === 0 ? (
        <div className="empty-state">No manifestos collected yet.</div>
      ) : (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Published</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {manifestos.map((manifesto) => (
                <tr key={manifesto.id}>
                  <td>{manifesto.title}</td>
                  <td>{manifesto.published_at ?? "—"}</td>
                  <td>
                    <Link to={`/manifestos/${manifesto.id}`}>Read</Link>
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
