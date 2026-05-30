import { type FormEvent, useEffect, useState } from "react";

import * as api from "../lib/api";
import type { Constituency } from "../lib/types";

export function ConstituenciesPage() {
  const [constituencies, setConstituencies] = useState<Constituency[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.listConstituencies({
          limit: 100,
          offset: 0,
          name: search || undefined,
        });
        setConstituencies(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load constituencies");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [search]);

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    setSearch(query.trim());
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h2>Constituencies</h2>
          <p>Parliamentary constituencies from collected election results.</p>
        </div>
      </div>

      <form className="toolbar" onSubmit={handleSearch}>
        <input
          className="input"
          placeholder="Search by constituency name"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button className="btn btn-primary" type="submit">
          Search
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading constituencies…</div>
      ) : (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>GSS code</th>
                <th>Country</th>
              </tr>
            </thead>
            <tbody>
              {constituencies.map((constituency) => (
                <tr key={constituency.id}>
                  <td>{constituency.name}</td>
                  <td>{constituency.gss_code ?? "—"}</td>
                  <td>{constituency.country ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
