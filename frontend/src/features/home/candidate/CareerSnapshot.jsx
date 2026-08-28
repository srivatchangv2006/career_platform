import Card from "../../../components/ui/Card";

export default function CareerSnapshot({
  applicationCount,
  interviewCount,
  connectionCount,
}) {
  const items = [
    {
      label: "Applications",
      value: applicationCount,
    },
    {
      label: "Interviews",
      value: interviewCount,
    },
    {
      label: "Connections",
      value: connectionCount,
    },
  ];

  return (
    <div className="dashboard-snapshot-grid">
      {items.map((item) => (
        <Card
          key={item.label}
          className="dashboard-stat-card"
        >
          <span className="dashboard-stat-label">
            {item.label}
          </span>

          <strong className="dashboard-stat-value">
            {item.value}
          </strong>
        </Card>
      ))}
    </div>
  );
}
