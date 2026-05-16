export default function ValidationStatus({ status, iq, oq, pq }) {
  const statusMap = {
    not_started: "badge-not_started",
    in_progress: "badge-in_progress",
    validated: "badge-validated",
    requires_revalidation: "badge-requires_revalidation",
  };

  return (
    <div>
      <span className={`badge ${statusMap[status] || "badge-not_started"}`}>
        {status?.replace(/_/g, " ")}
      </span>
      <div className="progress-bar">
        <div className={`progress-step ${iq ? "complete" : "incomplete"}`} title="IQ" />
        <div className={`progress-step ${oq ? "complete" : "incomplete"}`} title="OQ" />
        <div className={`progress-step ${pq ? "complete" : "incomplete"}`} title="PQ" />
      </div>
    </div>
  );
}