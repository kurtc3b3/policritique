import { useEffect, useState } from "react";

import * as api from "../lib/api";
import type { Election, ElectionResult } from "../lib/types";

export function ElectionsPage() {
  const [elections, setElections] = useState<Election[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [results, setResults] = useState<ElectionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listElections(50, 0);
        setElections(data.items);
        if (data.items[0]) {
          setSelectedId(data.items[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load elections");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  useEffect(() => {
    if (!selectedId) return;

    async function loadResults() {
      setResultsLoading(true);
      try {
        const data = await api.listElectionResults(selectedId as number, 100, 0);
        setResults(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load results");
      } finally {
        setResultsLoading(false);
      }
    }

    void loadResults();
  }, [selectedId]);

  return (
    <>
      <div className="page-header">
        <div>
          <h2>Elections</h2>
          <p>General election results imported from Parliament psephology data.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading elections…</div>
      ) : (
        <>
          <div className="toolbar">
            <select
              className="select"
              value={selectedId ?? ""}
              onChange={(event) => setSelectedId(Number(event.target.value))}
            >
              {elections.map((election) => (
                <option key={election.id} value={election.id}>
                  {election.name}
                </option>
              ))}
            </select>
          </div>

          <div className="card">
            {resultsLoading ? (
              <div className="loading-state">Loading candidacies…</div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Votes</th>
                    <th>Share</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <tr key={result.id}>
                      <td>{result.candidate_name}</td>
                      <td>{result.votes?.toLocaleString() ?? "—"}</td>
                      <td>
                        {result.vote_share != null
                          ? `${(result.vote_share * 100).toFixed(1)}%`
                          : "—"}
                      </td>
                      <td>
                        {result.is_elected ? (
                          <span className="badge success">Elected</span>
                        ) : (
                          <span className="badge">Candidate</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </>
  );
}
