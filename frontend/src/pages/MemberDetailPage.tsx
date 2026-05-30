import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import * as api from "../lib/api";
import type { MemberDetail } from "../lib/types";

export function MemberDetailPage() {
  const { memberId } = useParams();
  const [member, setMember] = useState<MemberDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!memberId) return;
      try {
        const data = await api.getMember(Number(memberId));
        setMember(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load member");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [memberId]);

  if (loading) return <div className="loading-state">Loading member…</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!member) return <div className="empty-state">Member not found.</div>;

  return (
    <>
      <div className="page-header">
        <div>
          <h2>{member.display_name ?? member.name}</h2>
          <p>{member.is_current ? "Current MP" : "Former MP"}</p>
        </div>
        <Link className="btn btn-secondary" to="/members">
          Back to MPs
        </Link>
      </div>

      <div className="card card-body detail-grid">
        <dl>
          <dt>Parliament ID</dt>
          <dd>{member.parliament_member_id ?? "—"}</dd>
          <dt>Gender</dt>
          <dd>{member.gender ?? "—"}</dd>
          <dt>Collected</dt>
          <dd>{member.collected_at}</dd>
        </dl>
      </div>

      <div className="card" style={{ marginTop: "1rem" }}>
        <div className="card-body">
          <h3 style={{ marginTop: 0, color: "var(--blue-900)" }}>Contacts</h3>
          {member.contacts.length === 0 ? (
            <p className="empty-state">No contacts recorded.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Value</th>
                  <th>Primary</th>
                </tr>
              </thead>
              <tbody>
                {member.contacts.map((contact) => (
                  <tr key={contact.id}>
                    <td>{contact.contact_type}</td>
                    <td>{contact.value}</td>
                    <td>{contact.is_primary ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
