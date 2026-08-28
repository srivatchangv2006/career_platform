import Card from "../../../components/ui/Card";

export default function JobDetails({
  job,
  recommendation = null,
}) {
  if (!job) {
    return null;
  }

  const salary =
    job.salary_min != null ||
    job.salary_max != null
      ? `${job.currency || "USD"} ${
          job.salary_min ?? ""
        } - ${
          job.salary_max ?? ""
        }`
      : "Not specified";

  return (
    <>
      <Card className="job-details-header">
        <p className="eyebrow">
          {job.status}
        </p>

        <h1>
          {job.title}
        </h1>

        <p className="job-details-company">
          {job.company_name || "Company"}
        </p>

        <div className="job-card-meta">
          {job.location && (
            <span>
              {job.location}
            </span>
          )}

          {job.employment_type && (
            <span>
              {job.employment_type}
            </span>
          )}

          {job.experience_level && (
            <span>
              {job.experience_level}
            </span>
          )}
        </div>

        {recommendation && (
          <div className="job-detail-match">
            <strong>
              {Math.round(
                recommendation.match_score || 0,
              )}
              % match
            </strong>

            {recommendation.recommendation_reason && (
              <p>
                {recommendation.recommendation_reason}
              </p>
            )}
          </div>
        )}
      </Card>

      <Card className="job-details-section">
        <h2>
          About the role
        </h2>

        <p className="job-details-description">
          {job.description}
        </p>
      </Card>

      <Card className="job-details-section">
        <h2>
          Job information
        </h2>

        <div className="job-details-grid">
          <div>
            <span>
              Company
            </span>

            <strong>
              {job.company_name ||
                "Company"}
            </strong>
          </div>

          <div>
            <span>
              Location
            </span>

            <strong>
              {job.location ||
                "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Employment
            </span>

            <strong>
              {job.employment_type ||
                "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Experience
            </span>

            <strong>
              {job.experience_level ||
                "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Salary
            </span>

            <strong>
              {salary}
            </strong>
          </div>

          <div>
            <span>
              Application deadline
            </span>

            <strong>
              {job.application_deadline ||
                "No deadline"}
            </strong>
          </div>
        </div>
      </Card>
    </>
  );
}
