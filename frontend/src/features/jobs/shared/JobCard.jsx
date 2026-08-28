import { Link } from "react-router-dom";

import Card from "../../../components/ui/Card";

export default function JobCard({
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
      : null;

  return (
    <Card className="job-card">
      <div className="job-card-header">
        <div>
          <h3 className="job-card-title">
            {job.title}
          </h3>

          <p className="job-card-company">
            {job.company_name || "Company"}
          </p>
        </div>

        {recommendation && (
          <div className="job-match-badge">
            {Math.round(
              recommendation.match_score || 0,
            )}
            % match
          </div>
        )}
      </div>

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

      {salary && (
        <p className="job-card-salary">
          {salary}
        </p>
      )}

      {recommendation?.recommendation_reason && (
        <p className="job-card-reason">
          {recommendation.recommendation_reason}
        </p>
      )}

      <Link
        to={`/jobs/${job.id}`}
        className="job-card-link"
      >
        View job
      </Link>
    </Card>
  );
}
