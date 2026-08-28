import Card from "../../../components/ui/Card";

export default function ApplicationPipeline({
  counts,
}) {
  const stages = [
    "APPLIED",
    "SCREENING",
    "ASSESSMENT",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
  ];

  return (
    <Card className="dashboard-section-card">
      <div className="dashboard-section-header">
        <div>
          <p className="eyebrow">
            Hiring pipeline
          </p>

          <h2>
            Application pipeline
          </h2>
        </div>
      </div>

      <div className="pipeline-list">
        {stages.map((stage) => (
          <div
            key={stage}
            className="pipeline-row"
          >
            <span>{stage}</span>

            <strong>
              {counts?.[stage] || 0}
            </strong>
          </div>
        ))}
      </div>
    </Card>
  );
}
