import {
  useEffect,
  useState,
} from "react";

import { useParams } from "react-router-dom";

import Card from "../components/ui/Card";
import Button from "../components/ui/Button";

import { useAuth } from "../hooks/useAuth";

import {
  getJob,
} from "../api/jobs.api";

import {
  getMyApplications,
} from "../api/applications.api";

import JobDetails from "../features/jobs/shared/JobDetails";
import ApplyForm from "../features/jobs/candidate/ApplyForm";

export default function JobDetailsPage() {
  const { jobId } = useParams();
  const { user } = useAuth();

  const [job, setJob] =
    useState(null);

  const [application, setApplication] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [
    showApplicationForm,
    setShowApplicationForm,
  ] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadJob() {
      setLoading(true);
      setError("");

      try {
        const jobResult =
          await getJob(jobId);

        if (!active) {
          return;
        }

        setJob(jobResult);

        if (
          user?.role === "CANDIDATE"
        ) {
          const applications =
            await getMyApplications();

          if (!active) {
            return;
          }

          const existingApplication =
            applications.find(
              (item) =>
                String(item.job_id) ===
                String(jobId),
            );

          setApplication(
            existingApplication ||
              null,
          );
        } else {
          setApplication(null);
        }
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load this job.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    // Load the selected job and application state.
    loadJob();

    return () => {
      active = false;
    };
  }, [jobId, user]);

  if (loading) {
    return (
      <Card className="feed-state">
        Loading job...
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="feed-state feed-error">
        {error}
      </Card>
    );
  }

  if (!job) {
    return (
      <Card className="feed-state">
        Job not found.
      </Card>
    );
  }

  if (user?.role === "CANDIDATE") {
    function handleApplied(
      createdApplication,
    ) {
      setApplication(
        createdApplication,
      );

      setShowApplicationForm(false);
    }

    const isOpen =
      job.status === "OPEN";

    return (
      <section className="job-details-page">
        <JobDetails job={job} />

        <Card className="job-application-card">
          {application ? (
            <>
              <p className="eyebrow">
                Application
              </p>

              <h2>
                Application submitted
              </h2>

              <p className="jobs-muted">
                You already applied to this
                position.
              </p>

              <div className="job-applied-status">
                Applied
              </div>
            </>
          ) : !isOpen ? (
            <>
              <p className="eyebrow">
                Applications
              </p>

              <h2>
                Applications are closed
              </h2>

              <p className="jobs-muted">
                This job is not currently open
                for applications.
              </p>
            </>
          ) : showApplicationForm ? (
            <ApplyForm
              jobId={job.id}
              onApplied={handleApplied}
            />
          ) : (
            <>
              <p className="eyebrow">
                Interested?
              </p>

              <h2>
                Apply for this role
              </h2>

              <p className="jobs-muted">
                Submit your application directly
                through MEDAI.
              </p>

              <Button
                onClick={() =>
                  setShowApplicationForm(
                    true,
                  )
                }
              >
                Apply now
              </Button>
            </>
          )}
        </Card>
      </section>
    );
  }

  return (
    <section className="job-details-page">
      <JobDetails job={job} />

      <Card className="job-application-card">
        <p className="eyebrow">
          Recruiter
        </p>

        <h2>
          Job posting
        </h2>

        <p className="jobs-muted">
          Recruiter job-management actions
          will be added here.
        </p>
      </Card>
    </section>
  );
}
