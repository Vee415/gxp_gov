const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Registry
  listSystems: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/systems/${query ? "?" + query : ""}`);
  },
  getSystem: (id) => request(`/systems/${id}`),
  createSystem: (data) => request("/systems/", { method: "POST", body: JSON.stringify(data) }),
  updateSystem: (id, data) => request(`/systems/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSystem: (id) => request(`/systems/${id}`, { method: "DELETE" }),

  // Classifier
  classify: (useCase, description = "") =>
    request("/classify/", { method: "POST", body: JSON.stringify({ use_case: useCase, description }) }),
  classifySystem: (id) => request(`/classify/${id}`, { method: "POST" }),
  classifyAndApply: (id) => request(`/classify/${id}/apply`, { method: "POST" }),

  // Behavioral Scenarios
  getBehavioralScenarios: (riskTier = "") => {
    const query = riskTier ? `?risk_tier=${riskTier}` : "";
    return request(`/classify/behavioral-scenarios${query}`);
  },

  // Validation
  listValidation: () => request("/validation/"),
  getFlags: () => request("/validation/flags"),
  getSummary: () => request("/validation/summary"),
  updateValidation: (id, data) =>
    request(`/validation/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  // Obligations
  getObligations: (systemId) => request(`/systems/${systemId}/obligations`),
  getObligationProgress: (systemId) => request(`/systems/${systemId}/obligations/progress`),
  updateObligation: (systemId, obligationId, data) =>
    request(`/systems/${systemId}/obligations/${obligationId}`, { method: "PUT", body: JSON.stringify(data) }),

  // Validation Steps
  getValidationSteps: (systemId, phase = "") => {
    const query = phase ? `?phase=${phase}` : "";
    return request(`/systems/${systemId}/validation-steps${query}`);
  },
  updateValidationStep: (systemId, stepId, data) =>
    request(`/systems/${systemId}/validation-steps/${stepId}`, { method: "PUT", body: JSON.stringify(data) }),
  recalculatePhaseStatus: (systemId) =>
    request(`/systems/${systemId}/validation-steps/recalculate`, { method: "POST" }),
  getValidationDetail: (systemId) => request(`/systems/${systemId}/validation/detail`),

  // Change Control
  getAuditLog: (systemId, entityType = "") => {
    const query = entityType ? `?entity_type=${entityType}` : "";
    return request(`/systems/${systemId}/audit-log${query}`);
  },
  recordVersionChange: (systemId, data) =>
    request(`/systems/${systemId}/version-change`, { method: "POST", body: JSON.stringify(data) }),
};