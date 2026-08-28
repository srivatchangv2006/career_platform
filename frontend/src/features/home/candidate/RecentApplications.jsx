import Card from "../../../components/ui/Card";
import Badge from "../../../components/ui/Badge";

export default function RecentApplications({
  applications,
  loading,
}) {
  return (
    <Card className="dashboard-section-card">
      <div className="dashboard-section-header">
        <div>
          <p className="eyebrow">
            Career activity
          </p>

          <h2>
            Recent applications
          </h2>
        </div>
      </div>

      {loading && (
        <p className="dashboard-muted">
          Loading applications...
        </p>
      )}

      {!loading &&
        applications.length === 0 && (
          <p className="dashboard-muted">
            You haven't applied to any jobs yet.
          </p>
        )}

      <div className="dashboard-application-list">
        {applications
          .slice(0, 5)
          .map((application) => (
            <article
              key={application.id}
              className="dashboard-application-item"
            >
              <div>
                <h3>
                  {application.job_title ||
                    "Job application"}
                </h3>

                <p>
                  {application.applied_at
                    ? new Date(
                        application.applied_at,
                      ).toLocaleDateString()
                    : ""}
                </p>
              </div>

              <Badge>
                {application.status ||
                  "APPLIED"}
              </Badge>
            </article>
          ))}
      </div>
    </Card>
  );
}
