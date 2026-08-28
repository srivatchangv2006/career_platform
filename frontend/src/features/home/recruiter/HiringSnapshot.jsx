import Card from "../../../components/ui/Card";

export default function HiringSnapshot({
  totalJobs,
  openJobs,
  totalApplications,
  upcomingInterviews,
}) {
  const items = [
    {
      label: "Total Jobs",
      value: totalJobs,
    },
    {
      label: "Open Jobs",
      value: openJobs,
    },
    {
      label: "Applicants",
      value: totalApplications,
    },
    {
      label: "Upcoming Interviews",
      value: upcomingInterviews,
    },
  ];

  return (
    <div className="dashboard-snapshot-grid dashboard-snapshot-grid-recruiter">
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
