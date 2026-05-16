import { useState, useEffect } from "react";
import { api } from "../api/client";
import RiskBadge from "../components/RiskBadge";
import ComplianceProgressBar from "../components/ComplianceProgressBar";
import ValidationChecklist from "../components/ValidationChecklist";
import ObligationTracker from "../components/ObligationTracker";

export default function ValidationTracker() {
  const [summary, setSummary] = useState(null);
  const [flags, setFlags] = useState([]);
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSystem, setExpandedSystem] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    try {
      const [summaryData, flagsData, systemsData] = await Promise.all([
        api.getSummary(),
        api.getFlags(),
        api.listValidation(),
      ]);
      setSummary(summaryData);
      setFlags(flagsData);
      setSystems(systemsData);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  async function loadDetail(systemId) {
    if (expandedSystem === systemId) {
      setExpandedSystem(null);
      setDetail(null);
      return;
    }
    setExpandedSystem(systemId);
    setDetailLoading(true);
    try {
      const data = await api.getValidationDetail(systemId);
      setDetail(data);
    } catch (e) {
      console.error("Failed to load detail:", e);
      setDetail(null);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleStepUpdate() {
    if (expandedSystem) {
      const data = await api.getValidationDetail(expandedSystem);
      setDetail(data);
    }
    loadData();
  }

  async function handleObligationUpdate() {
    if (expandedSystem) {
      const data = await api.getValidationDetail(expandedSystem);
      setDetail(data);
    }
    loadData();
  }

  if (loading) return <div className="loading">Loading validation data...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Validation Tracker</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24, fontSize: 14 }}>
        Track GxP validation lifecycle (IQ/OQ/PQ) for every AI system. Click a system to view
        obligations and validation steps. Systems running in production without completed validation
        are flagged as compliance risks.
      </p>

      {summary && (
        <div className="summary-grid">
          <div className="summary-card">
            <div className="number">{summary.total_systems}</div>
            <div className="label">Total Systems</div>
          </div>
          <div className="summary-card">
            <div className="number" style={{ color: "var(--success)" }}>{summary.validated}</div>
            <div className="label">Validated</div>
          </div>
          <div className="summary-card">
            <div className="number" style={{ color: "var(--warning)" }}>{summary.in_progress}</div>
            <div className="label">In Progress</div>
          </div>
          <div className="summary-card">
            <div className="number">{summary.not_started}</div>
            <div className="label">Not Started</div>
          </div>
          <div className="summary-card">
            <div className="number" style={{ color: "var(--danger)" }}>{summary.flagged}</div>
            <div className="label">Flagged</div>
          </div>
        </div>
      )}

      {flags.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ fontSize: 16, marginBottom: 12 }}>Compliance Flags</h3>
          {flags.map((flag) => (
            <div key={flag.id} className={`flag-item ${flag.severity === "critical" ? "flag-critical" : "flag-warning"}`}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>{flag.name}</strong>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <RiskBadge tier={flag.risk_tier} />
                  <span className={`badge badge-${flag.validation_status}`}>
                    {flag.validation_status?.replace(/_/g, " ")}
                  </span>
                </div>
              </div>
              <div className="flag-issues" style={{ marginTop: 8 }}>
                {flag.issues.map((issue, i) => (
                  <span key={i} className="flag-issue-tag">{issue}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <h3 style={{ fontSize: 16, marginBottom: 12 }}>All Systems</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>System</th>
              <th>Risk</th>
              <th>Status</th>
              <th>IQ</th>
              <th>OQ</th>
              <th>PQ</th>
              <th>Next Review</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <>
                <tr
                  key={s.id}
                  onClick={() => loadDetail(s.id)}
                  style={{ cursor: "pointer" }}
                  className={
                    !s.oq_complete && s.validation_status !== "not_started" ? "row-critical" :
                    s.validation_status === "requires_revalidation" ? "row-warning" : ""
                  }
                >
                  <td>
                    <strong>{s.name}</strong>
                    <span style={{ color: "var(--text-secondary)", fontSize: 12, marginLeft: 8 }}>
                      {s.vendor} v{s.version}
                    </span>
                  </td>
                  <td><RiskBadge tier={s.risk_tier} /></td>
                  <td>
                    <span className={`badge badge-${s.validation_status}`}>
                      {s.validation_status?.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className={s.iq_complete ? "status-complete" : "status-incomplete"}>
                    {s.iq_complete ? "✓" : "✗"}
                  </td>
                  <td className={s.oq_complete ? "status-complete" : "status-incomplete"}>
                    {s.oq_complete ? "✓" : "✗"}
                  </td>
                  <td className={s.pq_complete ? "status-complete" : "status-incomplete"}>
                    {s.pq_complete ? "✓" : "✗"}
                  </td>
                  <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                    {s.next_review_date || "Not set"}
                  </td>
                </tr>
                {expandedSystem === s.id && (
                  <tr key={`${s.id}-detail`}>
                    <td colSpan={7} style={{ padding: 0 }}>
                      <div className="system-detail-panel">
                        {detailLoading ? (
                          <div className="loading">Loading detail...</div>
                        ) : detail ? (
                          <>
                            {detail.obligation_progress && detail.obligation_progress.total > 0 && (
                              <div className="detail-section">
                                <h4>Obligation Progress ({detail.obligation_progress.total} obligations)</h4>
                                <ObligationTracker
                                  progress={detail.obligation_progress}
                                  systemId={s.id}
                                  onUpdate={handleObligationUpdate}
                                />
                              </div>
                            )}
                            {detail.phases && Object.values(detail.phases).some(p => p.length > 0) && (
                              <div className="detail-section">
                                <h4>Validation Steps</h4>
                                <ValidationChecklist
                                  steps={Object.values(detail.phases).flat()}
                                  systemId={s.id}
                                  onUpdate={handleStepUpdate}
                                />
                              </div>
                            )}
                            {(!detail.obligation_progress || detail.obligation_progress.total === 0) &&
                             (!detail.phases || Object.values(detail.phases).every(p => p.length === 0)) && (
                              <div className="empty-state">
                                No validation detail available. Classify this system to create obligations and steps.
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="empty-state">
                            No validation detail available. Classify this system to create obligations and steps.
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}