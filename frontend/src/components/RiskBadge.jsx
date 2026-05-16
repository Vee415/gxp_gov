export default function RiskBadge({ tier }) {
  const classMap = {
    UNACCEPTABLE: "badge-unacceptable",
    HIGH: "badge-high",
    LIMITED: "badge-limited",
    MINIMAL: "badge-minimal",
  };
  return <span className={`badge ${classMap[tier] || "badge-minimal"}`}>{tier}</span>;
}