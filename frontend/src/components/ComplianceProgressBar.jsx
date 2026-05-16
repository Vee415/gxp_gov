export default function ComplianceProgressBar({ total, complete, inProgress, notStarted }) {
  if (total === 0) return null;

  const completePct = (complete / total) * 100;
  const inProgressPct = (inProgress / total) * 100;
  const notStartedPct = (notStarted / total) * 100;
  const overallPct = Math.round((complete / total) * 100);

  return (
    <div className="compliance-progress">
      <div className="compliance-progress-bar">
        {completePct > 0 && (
          <div className="compliance-progress-segment complete" style={{ width: `${completePct}%` }} />
        )}
        {inProgressPct > 0 && (
          <div className="compliance-progress-segment in-progress" style={{ width: `${inProgressPct}%` }} />
        )}
        {notStartedPct > 0 && (
          <div className="compliance-progress-segment not-started" style={{ width: `${notStartedPct}%` }} />
        )}
      </div>
      <div className="compliance-progress-labels">
        <span className="progress-label complete">{complete} complete</span>
        <span className="progress-label in-progress">{inProgress} in progress</span>
        <span className="progress-label not-started">{notStarted} not started</span>
        <span className="progress-pct">{overallPct}%</span>
      </div>
    </div>
  );
}