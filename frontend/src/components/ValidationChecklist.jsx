import { useState } from "react";
import { api } from "../api/client";

export default function ValidationChecklist({ steps, systemId, onUpdate }) {
  const [updatingStep, setUpdatingStep] = useState(null);

  async function handleStepToggle(step) {
    const newStatus = step.status === "complete" ? "not_started" : "complete";
    setUpdatingStep(step.id);
    try {
      await api.updateValidationStep(systemId, step.id, { status: newStatus });
      if (onUpdate) onUpdate();
    } catch (e) {
      console.error("Failed to update step:", e);
    } finally {
      setUpdatingStep(null);
    }
  }

  const phases = ["IQ", "OQ", "PQ"];
  const phaseLabels = { IQ: "Installation Qualification", OQ: "Operational Qualification", PQ: "Performance Qualification" };

  const phasesWithSteps = phases.map((phase) => ({
    phase,
    label: phaseLabels[phase],
    steps: (steps || []).filter((s) => s.phase === phase).sort((a, b) => a.sort_order - b.sort_order),
  })).filter((p) => p.steps.length > 0);

  return (
    <div className="validation-checklist">
      {phasesWithSteps.map(({ phase, label, steps: phaseSteps }) => {
        const completed = phaseSteps.filter((s) => s.status === "complete").length;
        const total = phaseSteps.length;
        const allDone = completed === total;

        return (
          <div key={phase} className="checklist-phase">
            <div className="checklist-phase-header">
              <h5>{phase} — {label}</h5>
              <span className={`phase-count ${allDone ? "all-done" : ""}`}>
                {completed}/{total} complete
              </span>
            </div>
            {phaseSteps.map((step) => (
              <div key={step.id} className={`checklist-item ${step.status}`}>
                <label className="checklist-label">
                  <input
                    type="checkbox"
                    checked={step.status === "complete"}
                    disabled={updatingStep === step.id}
                    onChange={() => handleStepToggle(step)}
                  />
                  <span className="checklist-text">{step.step_label}</span>
                  {step.source && <span className="checklist-source">({step.source})</span>}
                </label>
                {step.status === "complete" && step.completed_at && (
                  <span className="checklist-date">Completed {step.completed_at}</span>
                )}
                {step.status === "in_progress" && (
                  <span className="checklist-badge in-progress">In Progress</span>
                )}
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}