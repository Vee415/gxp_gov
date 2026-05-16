import { useState } from "react";
import { api } from "../api/client";
import ComplianceProgressBar from "./ComplianceProgressBar";

export default function ObligationTracker({ obligations, progress, systemId, onUpdate }) {
  const [updatingId, setUpdatingId] = useState(null);

  async function handleStatusChange(obligationId, newStatus) {
    setUpdatingId(obligationId);
    try {
      await api.updateObligation(systemId, obligationId, { status: newStatus });
      if (onUpdate) onUpdate();
    } catch (e) {
      console.error("Failed to update obligation:", e);
    } finally {
      setUpdatingId(null);
    }
  }

  const statusOptions = ["not_started", "in_progress", "complete"];
  const statusLabels = { not_started: "Not Started", in_progress: "In Progress", complete: "Complete" };

  return (
    <div className="obligation-tracker">
      {progress && (
        <div style={{ marginBottom: 16 }}>
          <ComplianceProgressBar
            total={progress.total}
            complete={progress.complete}
            inProgress={progress.in_progress}
            notStarted={progress.not_started}
          />
        </div>
      )}
      <div className="obligation-list">
        {(obligations || []).map((obl) => (
          <div key={obl.id} className={`obligation-row ${obl.status}`}>
            <div className="obligation-header">
              <span className="obligation-article">{obl.article}</span>
              <select
                value={obl.status}
                disabled={updatingId === obl.id}
                onChange={(e) => handleStatusChange(obl.id, e.target.value)}
                className={`obligation-status-select ${obl.status}`}
              >
                {statusOptions.map((opt) => (
                  <option key={opt} value={opt}>{statusLabels[opt]}</option>
                ))}
              </select>
            </div>
            <p className="obligation-text">{obl.obligation}</p>
            <div className="obligation-meta">
              <span className="obligation-category">{obl.category.replace(/-/g, " ")}</span>
              {obl.required && <span className="obligation-required">Required</span>}
              {obl.evidence_ref && <span className="obligation-evidence">Evidence: {obl.evidence_ref}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}