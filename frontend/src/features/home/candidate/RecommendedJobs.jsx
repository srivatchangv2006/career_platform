import Card from "../../../components/ui/Card";

export default function RecommendedJobs({
  jobs,
  loading,
}) {
  return (
    <Card className="dashboard-section-card">
      <div className="dashboard-section-header">
        <div>
          <p className="eyebrow">
            Opportunities
          </p>

          <h2>
            Recommended for you
          </h2>
        </div>
      </div>

      {loading && (
        <p className="dashboard-muted">
          Loading recommendations...
        </p>
      )}

      {!loading && jobs.length === 0 && (
        <p className="dashboard-muted">
          No recommendations available yet.
        </p>
      )}

      <div className="dashboard-job-list">
        {jobs.slice(0, 5).map((job) => (
          <article
            key={job.id}
            className="dashboard-job-item"
          >
            <div>
              <h3>{job.title}</h3>

              <p>
                {job.location ||
                  "Location not specified"}
              </p>
            </div>

            <span>
              {job.employment_type ||
                "Opportunity"}
            </span>
          </article>
        ))}
      </div>
    </Card>
  );
}
