import { useState, useEffect } from "react";
import { api } from "../api/client";
import RiskBadge from "../components/RiskBadge";

export default function RiskClassifier() {
  const [systems, setSystems] = useState([]);
  const [mode, setMode] = useState("custom"); // "custom" or "existing"
  const [selectedSystemId, setSelectedSystemId] = useState("");
  const [useCase, setUseCase] = useState("");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [applyResult, setApplyResult] = useState(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    api.listSystems().then(setSystems).catch(() => {});
  }, []);

  async function handleClassify(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let data;
      if (mode === "existing" && selectedSystemId) {
        data = await api.classifySystem(selectedSystemId);
      } else {
        data = await api.classify(useCase, description);
      }
      setResult(data);
      // Fetch behavioral scenarios relevant to this risk tier
      if (data.risk_tier && data.risk_tier !== "UNACCEPTABLE") {
        try {
          const scenariosData = await api.getBehavioralScenarios(data.risk_tier);
          setScenarios(scenariosData);
        } catch { setScenarios([]); }
      } else {
        setScenarios([]);
      }
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  async function handleApply() {
    if (!selectedSystemId) return;
    setApplying(true);
    setApplyResult(null);
    try {
      const data = await api.classifyAndApply(selectedSystemId);
      setApplyResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setApplying(false);
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>EU AI Act Risk Classifier</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24, fontSize: 14 }}>
        Classify an AI system's risk tier under the EU AI Act. Rule-based, fully explainable — every
        classification includes the specific article or annex that triggered it.
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          <button
            className={`btn ${mode === "custom" ? "btn-primary" : ""}`}
            onClick={() => setMode("custom")}
          >
            Classify new use case
          </button>
          <button
            className={`btn ${mode === "existing" ? "btn-primary" : ""}`}
            onClick={() => setMode("existing")}
          >
            Classify existing system
          </button>
        </div>

        <form onSubmit={handleClassify}>
          {mode === "existing" ? (
            <div className="form-group">
              <label>Select System from Registry</label>
              <select
                value={selectedSystemId}
                onChange={(e) => setSelectedSystemId(e.target.value)}
                required
              >
                <option value="">— Select a system —</option>
                {systems.map((s) => (
                  <option key={s.id} value={s.id}>{s.name} — {s.use_case}</option>
                ))}
              </select>
            </div>
          ) : (
            <>
              <div className="form-group">
                <label>Use Case Description</label>
                <input
                  value={useCase}
                  onChange={(e) => setUseCase(e.target.value)}
                  placeholder="e.g. Patient stratification for oncology clinical trials"
                  required
                />
              </div>
              <div className="form-group">
                <label>Additional Description (optional)</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="More details about the AI system's purpose and context..."
                />
              </div>
            </>
          )}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Classifying..." : "Classify Risk"}
          </button>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="classification-result">
          <h3>Classification Result</h3>

          <div className={`tier-display ${result.risk_tier === "UNACCEPTABLE" ? "badge-unacceptable" : result.risk_tier === "HIGH" ? "badge-high" : result.risk_tier === "LIMITED" ? "badge-limited" : "badge-minimal"}`}>
            {result.risk_tier} RISK — Annex {result.annex}
          </div>

          {result.system_name && (
            <p style={{ marginBottom: 12, fontSize: 14 }}>
              System: <strong>{result.system_name}</strong>
            </p>
          )}

          <div style={{ marginBottom: 20 }}>
            <h4 style={{ fontSize: 14, marginBottom: 8 }}>Triggered Rules</h4>
            <ul style={{ listStyle: "none", padding: 0 }}>
              {result.triggered_rules.map((rule, i) => (
                <li key={i} style={{ padding: "4px 0", fontSize: 13, color: "var(--text-secondary)" }}>
                  {rule}
                </li>
              ))}
            </ul>
          </div>

          <div style={{ marginBottom: 20 }}>
            <h4 style={{ fontSize: 14, marginBottom: 8 }}>
              Obligations ({result.obligations.length})
            </h4>
            <ul className="obligations-list">
              {result.obligations.map((ob, i) => (
                <li key={i}>{ob}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 style={{ fontSize: 14, marginBottom: 8 }}>Gap Analysis</h4>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 8 }}>
              Status: <strong>{result.gap_analysis.status.replace(/_/g, " ")}</strong>
            </p>
            {result.gap_analysis.gaps.length > 0 && (
              <div>
                <p style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Gaps identified:</p>
                {result.gap_analysis.gaps.map((gap, i) => (
                  <div key={i} className="gap-item">{gap}</div>
                ))}
              </div>
            )}
          </div>

          {scenarios.length > 0 && (
            <div style={{ marginTop: 24, borderTop: "1px solid var(--border)", paddingTop: 20 }}>
              <h4 style={{ fontSize: 14, marginBottom: 4 }}>
                Behavioral Assessment Scenarios
              </h4>
              <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 12 }}>
                These scenarios help you question whether the vendor's stated purpose matches what the system actually does.
                Vendors often describe systems conservatively — use these questions to identify hidden risk.
              </p>
              {scenarios.map((s) => (
                <div key={s.id} className="card" style={{ marginBottom: 12, padding: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{s.title}</h5>
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 10, lineHeight: 1.5 }}>
                    {s.scenario}
                  </p>
                  <div style={{ marginBottom: 8 }}>
                    <p style={{ fontSize: 11, fontWeight: 600, marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5, color: "var(--text-secondary)" }}>
                      Questions to ask
                    </p>
                    {s.questions.map((q, i) => (
                      <p key={i} style={{ fontSize: 12, margin: "2px 0", paddingLeft: 8, borderLeft: "2px solid var(--border)" }}>
                        {q}
                      </p>
                    ))}
                  </div>
                  <div style={{ background: "rgba(234, 179, 8, 0.08)", border: "1px solid rgba(234, 179, 8, 0.2)", borderRadius: 6, padding: "8px 10", marginBottom: 6 }}>
                    <p style={{ fontSize: 11, fontWeight: 600, color: "#b45309", marginBottom: 2 }}>Risk indicator</p>
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: 0, lineHeight: 1.4 }}>{s.risk_indicator}</p>
                  </div>
                  <p style={{ fontSize: 11, color: "var(--text-secondary)", fontStyle: "italic" }}>
                    {s.likely_misclassification}
                  </p>
                </div>
              ))}
            </div>
          )}

          {mode === "existing" && selectedSystemId && (
            <div style={{ marginTop: 24, borderTop: "1px solid var(--border)", paddingTop: 20 }}>
              <button
                className="btn btn-primary"
                onClick={handleApply}
                disabled={applying}
              >
                {applying ? "Applying..." : "Apply to System"}
              </button>
              <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 8 }}>
                Persist this classification to the system: update risk tier, create obligations and validation steps.
              </p>
              {applyResult && (
                <div className="card" style={{ marginTop: 12, padding: 16, borderLeft: "3px solid var(--success)" }}>
                  <p style={{ fontWeight: 600, marginBottom: 8 }}>Classification Applied</p>
                  <p style={{ fontSize: 13 }}>
                    {applyResult.obligations_created} obligations created, {applyResult.validation_steps_created} validation steps created.
                  </p>
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                    View progress in the <a href="/validation" style={{ color: "var(--primary)" }}>Validation Tracker</a>.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}