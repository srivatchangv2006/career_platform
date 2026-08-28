import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getApplicationWorkspace,
} from "../../api/applications.api";

import {
  getInterview,
  getInterviewPreparation,
  prepareInterview,
} from "../../api/interviews.api";

export default function InterviewDetailsPage() {
  const { interviewId } =
    useParams();

  const [interview, setInterview] =
    useState(null);

  const [preparation, setPreparation] =
    useState(null);

  const [workspace, setWorkspace] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [preparing, setPreparing] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const result =
          await getInterview(
            interviewId,
          );

        const workspaceResult =
          await getApplicationWorkspace(
            result.application_id,
          );

        let preparationResult = null;

        try {
          preparationResult =
            await getInterviewPreparation(
              interviewId,
            );
        } catch {
          preparationResult = null;
        }

        if (!active) {
          return;
        }

        setInterview(result);
        setWorkspace(
          workspaceResult,
        );
        setPreparation(
          preparationResult,
        );
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load interview.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      active = false;
    };
  }, [interviewId]);

  async function handlePrepare() {
    setPreparing(true);
    setError("");

    try {
      const result =
        await prepareInterview(
          interviewId,
        );

      setPreparation(result);
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
        setError(
          "MEDAI Interview Preparation is temporarily unavailable because the AI usage limit has been reached. Your interview is still scheduled.",
        );
      } else {
        setError(
          detail ||
            "Unable to generate interview preparation.",
        );
      }
    } finally {
      setPreparing(false);
    }
  }

  if (loading) {
    return (
      <Card className="feed-state">
        Loading interview...
      </Card>
    );
  }

  if (error && !interview) {
    return (
      <Card className="feed-state feed-error">
        {error}
      </Card>
    );
  }

  if (!interview) {
    return (
      <Card className="feed-state">
        Interview not found.
      </Card>
    );
  }

  return (
    <section className="interview-details-page">
      <Link
        to="/interviews"
        className="interview-back-link"
      >
        ← Back to interviews
      </Link>

      <Card className="interview-details-hero">
        <p className="eyebrow">
          {interview.interview_type}
        </p>

        <h1>
          {workspace?.job?.title ||
            "Your interview"}
        </h1>

        <p className="interview-company-name">
          {workspace?.job?.company_name ||
            "Company"}
        </p>

        <span className="interview-status">
          {interview.status}
        </span>
      </Card>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <div className="interview-details-grid">
        <Card className="interview-details-card">
          <p className="eyebrow">
            Schedule
          </p>

          <h2>
            Interview details
          </h2>

          <div className="interview-info-list">
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

          {interview.notes && (
            <div className="interview-notes-box">
              <span>
                Notes
              </span>

              <p>
                {interview.notes}
              </p>
            </div>
          )}
        </Card>

        <Card className="interview-details-card">
          <p className="eyebrow">
            MEDAI
          </p>

          <h2>
            Interview preparation
          </h2>

          {!preparation ? (
            <>
              <p className="jobs-muted">
                Prepare for this interview
                using your resume, skills,
                career context, and the job.
              </p>

              <Button
                disabled={preparing}
                onClick={
                  handlePrepare
                }
              >
                {preparing
                  ? "Preparing..."
                  : "Prepare with MEDAI"}
              </Button>
            </>
          ) : (
            <>
              <div className="preparation-section">
                <h3>
                  Likely questions
                </h3>

                {(preparation.questions ||
                  []).map(
                  (
                    question,
                    index,
                  ) => (
                    <div
                      key={`${index}-${question}`}
                      className="preparation-question"
                    >
                      <strong>
                        {index + 1}.
                      </strong>

                      <span>
                        {question}
                      </span>
                    </div>
                  ),
                )}
              </div>

              <div className="preparation-section">
                <h3>
                  Suggested answer guidance
                </h3>

                {(preparation.suggested_answers ||
                  []).map(
                  (
                    answer,
                    index,
                  ) => (
                    <div
                      key={`${index}-${answer}`}
                      className="preparation-answer"
                    >
                      {answer}
                    </div>
                  ),
                )}
              </div>

              <div className="preparation-section">
                <h3>
                  Your strengths
                </h3>

                <ul>
                  {(preparation.strengths ||
                    []).map(
                    (
                      strength,
                      index,
                    ) => (
                      <li
                        key={`${index}-${strength}`}
                      >
                        {strength}
                      </li>
                    ),
                  )}
                </ul>
              </div>

              <div className="preparation-section">
                <h3>
                  Improvement areas
                </h3>

                <ul>
                  {(
                    preparation.improvement_areas ||
                    []
                  ).map(
                    (
                      area,
                      index,
                    ) => (
                      <li
                        key={`${index}-${area}`}
                      >
                        {area}
                      </li>
                    ),
                  )}
                </ul>
              </div>

              <div className="preparation-section">
                <h3>
                  Recommendations
                </h3>

                <ul>
                  {(
                    preparation.recommendations ||
                    []
                  ).map(
                    (
                      recommendation,
                      index,
                    ) => (
                      <li
                        key={`${index}-${recommendation}`}
                      >
                        {recommendation}
                      </li>
                    ),
                  )}
                </ul>
              </div>

              <Button
                variant="secondary"
                disabled={preparing}
                onClick={
                  handlePrepare
                }
              >
                {preparing
                  ? "Regenerating..."
                  : "Regenerate preparation"}
              </Button>
            </>
          )}
        </Card>
      </div>
    </section>
  );
}
