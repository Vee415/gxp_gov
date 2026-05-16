import RiskBadge from "./RiskBadge";
import ValidationStatus from "./ValidationStatus";

export default function SystemCard({ system }) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 style={{ margin: 0 }}>{system.name}</h3>
          <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {system.vendor} &middot; v{system.version}
          </span>
        </div>
        <RiskBadge tier={system.risk_tier} />
      </div>
      <p style={{ fontSize: 14, color: "var(--text-secondary)", margin: "8px 0" }}>
        {system.use_case}
      </p>
      {system.description && (
        <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>
          {system.description}
        </p>
      )}
      <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <ValidationStatus
          status={system.validation_status}
          iq={system.iq_complete}
          oq={system.oq_complete}
          pq={system.pq_complete}
        />
        <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
          {system.owner || "No owner"}
        </span>
      </div>
    </div>
  );
}