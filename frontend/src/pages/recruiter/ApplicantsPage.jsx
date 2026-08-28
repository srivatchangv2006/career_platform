import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import Card from "../../components/ui/Card";
import {
  getMyJobs,
} from "../../api/jobs.api";

import {
  getRecruiterApplicants,
  updateRecruiterApplicationStatus,
} from "../../api/recruiterApplications.api";

export default function ApplicantsPage() {
  const [jobs, setJobs] =
    useState([]);

  const [applicants, setApplicants] =
    useState([]);

  const [selectedJobId, setSelectedJobId] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [updatingId, setUpdatingId] =
    useState("");

  const loadJobs =
    useCallback(async () => {
      try {
        const result =
          await getMyJobs();

        setJobs(
          Array.isArray(result)
            ? result
            : [],
        );
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your jobs.",
        );
      }
    }, []);

  const loadApplicants =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const result =
          await getRecruiterApplicants({
            jobId:
              selectedJobId,
            status:
              statusFilter,
            search,
          });

        setApplicants(
          Array.isArray(result)
            ? result
            : [],
        );
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load applicants.",
        );
      } finally {
        setLoading(false);
      }
    }, [
      selectedJobId,
      statusFilter,
      search,
    ]);

  useEffect(() => {
    // Load recruiter-owned jobs.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadJobs();
  }, [loadJobs]);

  useEffect(() => {
    const timeoutId =
      setTimeout(() => {
        loadApplicants();
      }, 250);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [loadApplicants]);

  async function handleStatusChange(
    applicationId,
    nextStatus,
  ) {
    setUpdatingId(
      applicationId,
    );
    setError("");

    try {
      const updated =
        await updateRecruiterApplicationStatus(
          applicationId,
          {
            status: nextStatus,
          },
        );

      setApplicants((current) =>
        current.map(
          (applicant) =>
            applicant.id ===
            updated.id
              ? {
                  ...applicant,
                  status:
                    updated.status,
                  updated_at:
                    updated.updated_at,
                }
              : applicant,
        ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update application status.",
      );
    } finally {
      setUpdatingId("");
    }
  }

  return (
    <section className="applicants-page">
      <div className="applicants-hero">
        <p className="eyebrow">
          Recruiter
        </p>

        <h1>
          Applicants
        </h1>

        <p>
          Review candidates who applied
          to your jobs, search the applicant
          pool, and manage their hiring
          stage.
        </p>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <Card className="applicants-filters-card">
        <div className="applicants-filters">
          <label>
            Job

            <select
              value={selectedJobId}
              onChange={(event) =>
                setSelectedJobId(
                  event.target.value,
                )
              }
            >
              <option value="">
                All jobs
              </option>

              {jobs.map((job) => (
                <option
                  key={job.id}
                  value={job.id}
                >
                  {job.title}
                </option>
              ))}
            </select>
          </label>

          <label>
            Status

            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value,
                )
              }
            >
              <option value="">
                All statuses
              </option>

              <option value="APPLIED">
                Applied
              </option>

              <option value="SCREENING">
                Screening
              </option>

              <option value="ASSESSMENT">
                Assessment
              </option>

              <option value="INTERVIEW">
                Interview
              </option>

              <option value="OFFER">
                Offer
              </option>

              <option value="REJECTED">
                Rejected
              </option>

              <option value="WITHDRAWN">
                Withdrawn
              </option>
            </select>
          </label>

          <label className="applicant-search-field">
            Search candidates

            <input
              type="search"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search by name or email..."
              aria-label="Search candidates"
            />
          </label>

          <div className="applicant-count">
            {applicants.length} applicant
            {applicants.length === 1
              ? ""
              : "s"}
          </div>
        </div>
      </Card>

      <Card className="applicants-list-card">
        <div className="applicants-list-header">
          <div>
            <p className="eyebrow">
              Candidate pipeline
            </p>

            <h2>
              Applicants
            </h2>
          </div>
        </div>

        {loading && (
          <p className="jobs-muted">
            Loading applicants...
          </p>
        )}

        {!loading &&
          applicants.length === 0 && (
            <div className="applicants-empty">
              <h3>
                No applicants found
              </h3>

              <p>
                Try another job, status,
                or candidate search.
              </p>
            </div>
          )}

        {!loading &&
          applicants.length > 0 && (
            <div className="applicants-list">
              {applicants.map(
                (applicant) => (
                  <article
                    key={applicant.id}
                    className="applicant-row"
                  >
                    <div className="applicant-main">
                      <div className="applicant-avatar">
                        {(applicant.candidate_name ||
                          applicant.candidate_email ||
                          "C")
                          .charAt(0)
                          .toUpperCase()}
                      </div>

                      <div className="applicant-info">
                        <h3>
                          {applicant.candidate_name ||
                            "Candidate"}
                        </h3>

                        <p>
                          {applicant.candidate_email}
                        </p>

                        <span>
                          {applicant.job_title}
                        </span>

                        <div className="applicant-links">
                          <Link
                            to={`/profile/${applicant.candidate_id}`}
                          >
                            View profile
                          </Link>

                          <Link
                            to={`/recruiter/applicants/${applicant.id}`}
                          >
                            View application
                          </Link>
                        </div>
                      </div>
                    </div>

                    <div className="applicant-actions">
                      <span
                        className={`applicant-status status-${String(
                          applicant.status,
                        ).toLowerCase()}`}
                      >
                        {applicant.status}
                      </span>

                      <select
                        value={
                          applicant.status
                        }
                        disabled={
                          updatingId ===
                          applicant.id
                        }
                        onChange={(event) =>
                          handleStatusChange(
                            applicant.id,
                            event.target.value,
                          )
                        }
                        aria-label={`Update application status for ${
                          applicant.candidate_name ||
                          applicant.candidate_email
                        }`}
                      >
                        <option
                          value={
                            applicant.status
                          }
                        >
                          {applicant.status}
                        </option>

                        {applicant.status ===
                          "APPLIED" && (
                          <>
                            <option value="SCREENING">
                              Screening
                            </option>

                            <option value="REJECTED">
                              Rejected
                            </option>
                          </>
                        )}

                        {applicant.status ===
                          "SCREENING" && (
                          <>
                            <option value="ASSESSMENT">
                              Assessment
                            </option>

                            <option value="INTERVIEW">
                              Interview
                            </option>

                            <option value="REJECTED">
                              Rejected
                            </option>
                          </>
                        )}

                        {applicant.status ===
                          "ASSESSMENT" && (
                          <>
                            <option value="INTERVIEW">
                              Interview
                            </option>

                            <option value="REJECTED">
                              Rejected
                            </option>
                          </>
                        )}

                        {applicant.status ===
                          "INTERVIEW" && (
                          <>
                            <option value="OFFER">
                              Offer
                            </option>

                            <option value="REJECTED">
                              Rejected
                            </option>
                          </>
                        )}

                        {applicant.status ===
                          "OFFER" && (
                          <option value="REJECTED">
                            Rejected
                          </option>
                        )}
                      </select>

                      <span className="applicant-date">
                        Applied{" "}
                        {applicant.applied_at
                          ? new Date(
                              applicant.applied_at,
                            ).toLocaleDateString()
                          : ""}
                      </span>
                    </div>
                  </article>
                ),
              )}
            </div>
          )}
      </Card>
    </section>
  );
}
