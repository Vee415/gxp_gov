import { useState, useEffect } from "react";
import { api } from "../api/client";
import RiskBadge from "../components/RiskBadge";
import ValidationStatus from "../components/ValidationStatus";

export default function Registry() {
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterTier, setFilterTier] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "", vendor: "", version: "", use_case: "", description: "",
    risk_tier: "MINIMAL", owner: "",
  });

  useEffect(() => { loadSystems(); }, []);

  async function loadSystems() {
    try {
      setLoading(true);
      const params = {};
      if (filterTier) params.risk_tier = filterTier;
      if (filterStatus) params.validation_status = filterStatus;
      const data = await api.listSystems(params);
      setSystems(data);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { loadSystems(); }, [filterTier, filterStatus]);

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await api.createSystem(form);
      setShowForm(false);
      setForm({ name: "", vendor: "", version: "", use_case: "", description: "", risk_tier: "MINIMAL", owner: "" });
      loadSystems();
    } catch (e) { setError(e.message); }
  }

  if (loading) return <div className="loading">Loading systems...</div>;

  return (
    <div>
      <div className="card-header" style={{ marginBottom: 24 }}>
        <h2>AI System Registry</h2>
        <div style={{ display: "flex", gap: 12 }}>
          <div className="filters">
            <select value={filterTier} onChange={(e) => setFilterTier(e.target.value)}>
              <option value="">All Risk Tiers</option>
              <option value="UNACCEPTABLE">Unacceptable</option>
              <option value="HIGH">High</option>
              <option value="LIMITED">Limited</option>
              <option value="MINIMAL">Minimal</option>
            </select>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="validated">Validated</option>
              <option value="requires_revalidation">Requires Revalidation</option>
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ Add System"}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Add New AI System</h3>
          <form onSubmit={handleCreate}>
            <div className="form-row">
              <div className="form-group">
                <label>System Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Vendor</label>
                <input value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Version</label>
                <input value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Risk Tier</label>
                <select value={form.risk_tier} onChange={(e) => setForm({ ...form, risk_tier: e.target.value })}>
                  <option value="MINIMAL">Minimal</option>
                  <option value="LIMITED">Limited</option>
                  <option value="HIGH">High</option>
                  <option value="UNACCEPTABLE">Unacceptable</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Use Case</label>
              <input value={form.use_case} onChange={(e) => setForm({ ...form, use_case: e.target.value })} required placeholder="e.g. Patient stratification for clinical trials" />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Owner</label>
              <input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} placeholder="e.g. Dr. Sarah Mueller" />
            </div>
            <button className="btn btn-primary" type="submit">Create System</button>
          </form>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>System</th>
              <th>Use Case</th>
              <th>Risk</th>
              <th>Validation</th>
              <th>Owner</th>
              <th>Next Review</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <tr key={s.id}>
                <td><strong>{s.name}</strong><br /><span style={{ fontSize: 12, color: "var(--text-secondary)" }}>{s.vendor} v{s.version}</span></td>
                <td style={{ maxWidth: 250, fontSize: 13 }}>{s.use_case}</td>
                <td><RiskBadge tier={s.risk_tier} /></td>
                <td><ValidationStatus status={s.validation_status} iq={s.iq_complete} oq={s.oq_complete} pq={s.pq_complete} /></td>
                <td style={{ fontSize: 13 }}>{s.owner || "—"}</td>
                <td style={{ fontSize: 13 }}>{s.next_review_date || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{ marginTop: 12, fontSize: 13, color: "var(--text-secondary)" }}>
        {systems.length} system{systems.length !== 1 ? "s" : ""} registered
      </p>
    </div>
  );
}