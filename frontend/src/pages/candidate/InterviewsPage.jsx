import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getMyInterviews,
  prepareInterview,
} from "../../api/interviews.api";

export default function InterviewsPage() {
  const navigate =
    useNavigate();

  const [interviews, setInterviews] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [preparingId, setPreparingId] =
    useState("");

  const [prepareError, setPrepareError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function loadInterviews() {
      setLoading(true);
      setError("");

      try {
        const result =
          await getMyInterviews();

        if (active) {
          setInterviews(
            Array.isArray(result)
              ? result
              : [],
          );
        }
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load your interviews.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadInterviews();

    return () => {
      active = false;
    };
  }, []);

  async function handlePrepare(
    interviewId,
  ) {
    setPreparingId(interviewId);
    setPrepareError("");

    try {
      await prepareInterview(
        interviewId,
      );

      navigate(
        `/interviews/${interviewId}`,
      );
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "";

      if (
        err?.response?.status ===
          429 ||
        detail
          .toLowerCase()
          .includes("quota") ||
        detail
          .toLowerCase()
          .includes("rate limit") ||
        detail
          .toLowerCase()
          .includes("resource exhausted")
      ) {
        setPrepareError(
          "MEDAI Interview Preparation is temporarily unavailable because the AI usage limit has been reached. You can try again later.",
        );
      } else {
        setPrepareError(
          detail ||
            "Unable to prepare for this interview.",
        );
      }
    } finally {
      setPreparingId("");
    }
  }

  if (loading) {
    return (
      <Card className="feed-state">
        Loading interviews...
      </Card>
    );
  }

  return (
    <section className="interviews-page">
      <div className="interviews-hero">
        <p className="eyebrow">
          Candidate
        </p>

        <h1>
          My Interviews
        </h1>

        <p>
          Keep track of your scheduled
          interviews and prepare with MEDAI.
        </p>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      {prepareError && (
        <div className="jobs-info-message">
          {prepareError}
        </div>
      )}

      {interviews.length === 0 &&
        !error && (
          <Card className="interviews-empty-card">
            <h2>
              No interviews yet
            </h2>

            <p>
              When a recruiter schedules an
              interview, it will appear here.
            </p>
          </Card>
        )}

      {interviews.length > 0 && (
        <div className="interviews-list">
          {interviews.map(
            (interview) => (
              <Card
                key={interview.id}
                className="interview-card"
              >
                <div className="interview-card-header">
                  <div>
                    <p className="eyebrow">
                      {interview.interview_type}
                    </p>

                    <h2>
                      Interview
                    </h2>
                  </div>

                  <span className="interview-status">
                    {interview.status}
                  </span>
                </div>

                <div className="interview-details-grid">
                  <div>
                    <span>
                      Date & time
                    </span>

                    <strong>
                      {interview.scheduled_at
                        ? new Date(
                            interview.scheduled_at,
                          ).toLocaleString()
                        : "Not scheduled"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Duration
                    </span>

                    <strong>
                      {interview.duration_minutes
                        ? `${interview.duration_minutes} minutes`
                        : "Not specified"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Location
                    </span>

                    <strong>
                      {interview.location ||
                        "Online"}
                    </strong>
                  </div>
                </div>

                {interview.notes && (
                  <p className="interview-notes">
                    {interview.notes}
                  </p>
                )}

                <div className="interview-card-actions">
                  {interview.meeting_url && (
                    <a
                      href={
                        interview.meeting_url
                      }
                      target="_blank"
                      rel="noreferrer"
                      className="interview-meeting-link"
                    >
                      Join interview
                    </a>
                  )}

                  <Button
                    variant="secondary"
                    disabled={
                      preparingId ===
                      interview.id
                    }
                    onClick={() =>
                      handlePrepare(
                        interview.id,
                      )
                    }
                  >
                    {preparingId ===
                    interview.id
                      ? "Preparing..."
                      : "Prepare with MEDAI"}
                  </Button>

                  <Link
                    to={`/interviews/${interview.id}`}
                    className="interview-details-link"
                  >
                    View interview
                  </Link>
                </div>
              </Card>
            ),
          )}
        </div>
      )}
    </section>
  );
}
