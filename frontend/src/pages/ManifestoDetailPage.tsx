import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import * as api from "../lib/api";
import type { ManifestoDetail } from "../lib/types";

export function ManifestoDetailPage() {
  const { manifestoId } = useParams();
  const [manifesto, setManifesto] = useState<ManifestoDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!manifestoId) return;
      try {
        const data = await api.getManifesto(Number(manifestoId));
        setManifesto(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load manifesto");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [manifestoId]);

  if (loading) return <div className="loading-state">Loading manifesto…</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!manifesto) return <div className="empty-state">Manifesto not found.</div>;

  return (
    <>
      <div className="page-header">
        <div>
          <h2>{manifesto.title}</h2>
          <p>{manifesto.published_at ?? "Publication date unknown"}</p>
        </div>
        <Link className="btn btn-secondary" to="/manifestos">
          Back to manifestos
        </Link>
      </div>

      <div className="card card-body detail-grid">
        <dl>
          <dt>Party ID</dt>
          <dd>{manifesto.party_id}</dd>
          <dt>Election ID</dt>
          <dd>{manifesto.election_id ?? "—"}</dd>
          <dt>Source</dt>
          <dd>
            {manifesto.source_url ? (
              <a href={manifesto.source_url} target="_blank" rel="noreferrer">
                {manifesto.source_url}
              </a>
            ) : (
              "—"
            )}
          </dd>
        </dl>
      </div>

      <div className="card" style={{ marginTop: "1rem" }}>
        <div className="card-body">
          <h3 style={{ marginTop: 0, color: "var(--blue-900)" }}>Text</h3>
          {manifesto.text ? (
            <div className="manifesto-text">{manifesto.text.slice(0, 12000)}</div>
          ) : (
            <p className="empty-state">No text available for this manifesto.</p>
          )}
        </div>
      </div>
    </>
  );
}
