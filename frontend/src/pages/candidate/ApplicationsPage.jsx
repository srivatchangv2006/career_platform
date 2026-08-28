import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { Link } from "react-router-dom";

import Card from "../../components/ui/Card";

import {
  getMyApplications,
} from "../../api/applications.api";

import {
  getJob,
} from "../../api/jobs.api";

export default function ApplicationsPage() {
  const [applications, setApplications] =
    useState([]);

  const [jobs, setJobs] =
    useState({});

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const loadApplications =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const result =
          await getMyApplications();

        const applicationList =
          Array.isArray(result)
            ? result
            : [];

        setApplications(
          applicationList,
        );

        const uniqueJobIds = [
          ...new Set(
            applicationList.map(
              (application) =>
                application.job_id,
            ),
          ),
        ];

        const jobEntries =
          await Promise.all(
            uniqueJobIds.map(
              async (jobId) => {
                try {
                  const job =
                    await getJob(
                      jobId,
                    );

                  return [
                    String(jobId),
                    job,
                  ];
                } catch {
                  return null;
                }
              },
            ),
          );

        const jobMap = {};

        for (const entry of jobEntries) {
          if (entry) {
            jobMap[entry[0]] =
              entry[1];
          }
        }

        setJobs(jobMap);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your applications.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Load applications when the page opens.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadApplications();
  }, [loadApplications]);

  const statusCounts =
    useMemo(() => {
      return applications.reduce(
        (counts, application) => {
          const status =
            application.status ||
            "UNKNOWN";

          counts[status] =
            (counts[status] || 0) + 1;

          return counts;
        },
        {},
      );
    }, [applications]);

  if (loading) {
    return (
      <section className="applications-page">
        <Card className="feed-state">
          Loading your applications...
        </Card>
      </section>
    );
  }

  return (
    <section className="applications-page">
      <div className="applications-hero">
        <p className="eyebrow">
          Candidate
        </p>

        <h1>
          My Applications
        </h1>

        <p>
          Track your applications and
          follow your progress across
          every opportunity.
        </p>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <div className="application-stat-grid">
        <Card className="application-stat-card">
          <span>
            Total
          </span>

          <strong>
            {applications.length}
          </strong>
        </Card>

        <Card className="application-stat-card">
          <span>
            Interviews
          </span>

          <strong>
            {statusCounts.INTERVIEW || 0}
          </strong>
        </Card>

        <Card className="application-stat-card">
          <span>
            Offers
          </span>

          <strong>
            {statusCounts.OFFER || 0}
          </strong>
        </Card>

        <Card className="application-stat-card">
          <span>
            Screening
          </span>

          <strong>
            {statusCounts.SCREENING || 0}
          </strong>
        </Card>
      </div>

      <Card className="applications-list-card">
        <div className="applications-list-header">
          <div>
            <p className="eyebrow">
              Career progress
            </p>

            <h2>
              Your applications
            </h2>
          </div>

          <span className="jobs-count">
            {applications.length}
          </span>
        </div>

        {applications.length === 0 && (
          <div className="applications-empty-state">
            <h3>
              No applications yet
            </h3>

            <p>
              When you apply to a job,
              your application will appear
              here.
            </p>
          </div>
        )}

        {applications.length > 0 && (
          <div className="applications-list">
            {applications.map(
              (application) => {
                const job =
                  jobs[
                    String(
                      application.job_id,
                    )
                  ];

                return (
                  <article
                    key={application.id}
                    className="application-row"
                  >
                    <div className="application-main">
                      <div className="application-icon">
                        JOB
                      </div>

                      <div>
                        <h3>
                          {job?.title ||
                            "Job application"}
                        </h3>

                        <p>
                          {job?.company_name ||
                            "Company"}
                        </p>

                        {job?.location && (
                          <span>
                            {job.location}
                          </span>
                        )}

                        <Link
                          to={`/applications/${application.id}`}
                          className="application-view-link"
                        >
                          View application →
                        </Link>
                      </div>
                    </div>

                    <div className="application-meta">
                      <span
                        className={`application-status status-${String(
                          application.status ||
                            "UNKNOWN",
                        ).toLowerCase()}`}
                      >
                        {application.status}
                      </span>

                      <span className="application-date">
                        {application.applied_at
                          ? new Date(
                              application.applied_at,
                            ).toLocaleDateString()
                          : ""}
                      </span>
                    </div>
                  </article>
                );
              },
            )}
          </div>
        )}
      </Card>
    </section>
  );
}
