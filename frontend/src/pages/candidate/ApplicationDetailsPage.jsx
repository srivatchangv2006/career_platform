import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getApplicationWorkspace,
  getApplicationTimeline,
  analyzeSkillGap,
} from "../../api/applications.api";

export default function ApplicationDetailsPage() {
  const { applicationId } =
    useParams();

  const navigate =
    useNavigate();

  const [workspace, setWorkspace] =
    useState(null);

  const [timeline, setTimeline] =
    useState([]);

  const [skillGap, setSkillGap] =
    useState(null);

  const [skillGapLoading, setSkillGapLoading] =
    useState(false);

  const [skillGapError, setSkillGapError] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function loadApplication() {
      setLoading(true);
      setError("");

      try {
        const [
          workspaceResult,
          timelineResult,
        ] = await Promise.all([
          getApplicationWorkspace(
            applicationId,
          ),
          getApplicationTimeline(
            applicationId,
          ),
        ]);

        if (!active) {
          return;
        }

        setWorkspace(
          workspaceResult,
        );

        setTimeline(
          Array.isArray(
            timelineResult?.events,
          )
            ? timelineResult.events
            : [],
        );
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load this application.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadApplication();

    return () => {
      active = false;
    };
  }, [applicationId]);

  if (loading) {
    return (
      <Card className="feed-state">
        Loading application...
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

  if (!workspace) {
    return (
      <Card className="feed-state">
        Application not found.
      </Card>
    );
  }

  const application =
    workspace.application;

  const job = workspace.job;
  const resume = workspace.resume;

  const applicationEvents =
    timeline.filter(
      (event) =>
        event.event_type ===
          "APPLICATION_SUBMITTED" ||
        event.event_type ===
          "STATUS_CHANGED" ||
        event.event_type ===
          "INTERVIEW_CREATED",
    );

  const aiEvents =
    timeline.filter(
      (event) =>
        event.event_type ===
          "JOB_RECOMMENDATION" ||
        event.event_type ===
          "SKILL_GAP_ANALYSIS" ||
        event.event_type ===
          "INTERVIEW_PREPARATION",
    );

  const currentSkillGap =
    skillGap ||
    workspace.skill_gap;

  async function handleSkillGapAnalysis() {
    setSkillGapLoading(true);
    setSkillGapError("");

    try {
      const result =
        await analyzeSkillGap(
          job.id,
        );

      setSkillGap(result);
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
        setSkillGapError(
          "MEDAI Skill Gap Analysis is temporarily unavailable because the AI usage limit has been reached. Your application is safe and you can try again later.",
        );
      } else {
        setSkillGapError(
          detail ||
            "Unable to generate Skill Gap Analysis.",
        );
      }
    } finally {
      setSkillGapLoading(false);
    }
  }

  return (
    <section className="application-details-page">
      <Button
        variant="ghost"
        onClick={() =>
          navigate("/applications")
        }
      >
        ← Back to applications
      </Button>

      <Card className="application-details-hero">
        <p className="eyebrow">
          Application
        </p>

        <h1>
          {job.title}
        </h1>

        <p className="application-company">
          {job.company_name ||
            "Company"}
        </p>

        <div className="application-detail-meta">
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

        <div className="application-current-status">
          {application.status}
        </div>
      </Card>

      <div className="application-details-grid">
        <div className="application-details-main">

          {/* APPLICATION TIMELINE */}

          <Card className="application-detail-card">
            <div className="application-detail-card-header">
              <div>
                <p className="eyebrow">
                  Progress
                </p>

                <h2>
                  Application timeline
                </h2>
              </div>
            </div>

            {applicationEvents.length ===
            0 ? (
              <p className="jobs-muted">
                No application progress
                events yet.
              </p>
            ) : (
              <div className="application-timeline">
                {applicationEvents.map(
                  (event, index) => (
                    <div
                      key={`${event.id}-${index}`}
                      className="application-timeline-item"
                    >
                      <div className="application-timeline-dot" />

                      <div className="application-timeline-content">
                        <div className="application-timeline-title-row">
                          <h3>
                            {event.title}
                          </h3>

                          {event.status && (
                            <span>
                              {event.status}
                            </span>
                          )}
                        </div>

                        {event.description && (
                          <p>
                            {event.description}
                          </p>
                        )}

                        <time>
                          {event.created_at
                            ? new Date(
                                event.created_at,
                              ).toLocaleString()
                            : ""}
                        </time>
                      </div>
                    </div>
                  ),
                )}
              </div>
            )}
          </Card>

          {/* MEDAI ACTIVITY */}

          {aiEvents.length > 0 && (
            <Card className="application-detail-card">
              <div className="application-detail-card-header">
                <div>
                  <p className="eyebrow">
                    MEDAI
                  </p>

                  <h2>
                    AI activity
                  </h2>

                  <p className="jobs-muted">
                    AI-powered activity related
                    to this opportunity.
                  </p>
                </div>
              </div>

              <div className="ai-insights-list">
                {aiEvents.map(
                  (event, index) => (
                    <div
                      key={`${event.id}-${index}`}
                      className="ai-insight-card"
                    >
                      <div className="ai-insight-icon">
                        AI
                      </div>

                      <div className="ai-insight-content">
                        <div className="ai-insight-title-row">
                          <h3>
                            {event.title}
                          </h3>

                          {event.status && (
                            <span>
                              {event.status}
                            </span>
                          )}
                        </div>

                        {event.description && (
                          <p>
                            {event.description}
                          </p>
                        )}

                        <time>
                          {event.created_at
                            ? new Date(
                                event.created_at,
                              ).toLocaleString()
                            : ""}
                        </time>
                      </div>
                    </div>
                  ),
                )}
              </div>
            </Card>
          )}

          {/* SKILL GAP ANALYSIS */}

          <Card className="application-detail-card">
            <p className="eyebrow">
              MEDAI
            </p>

            <h2>
              Skill Gap Analysis
            </h2>

            {currentSkillGap ? (
              <>
                {currentSkillGap
                  .overall_match_score !=
                  null && (
                  <div className="skill-gap-score">
                    {Math.round(
                      currentSkillGap
                        .overall_match_score,
                    )}
                    % match
                  </div>
                )}

                <div className="skill-gap-columns">
                  <div>
                    <h3>
                      Matched skills
                    </h3>

                    <div className="skill-tag-list">
                      {(
                        currentSkillGap
                          .matched_skills ||
                        []
                      ).map(
                        (skill) => (
                          <span
                            key={String(
                              skill,
                            )}
                          >
                            {String(
                              skill,
                            )}
                          </span>
                        ),
                      )}
                    </div>
                  </div>

                  <div>
                    <h3>
                      Skills to develop
                    </h3>

                    <div className="skill-tag-list">
                      {(
                        currentSkillGap
                          .missing_skills ||
                        []
                      ).map(
                        (skill) => (
                          <span
                            key={String(
                              skill,
                            )}
                          >
                            {String(
                              skill,
                            )}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                </div>

                {currentSkillGap
                  .recommendations
                  ?.length > 0 && (
                  <div className="skill-gap-recommendations">
                    <h3>
                      Recommendations
                    </h3>

                    <ul>
                      {currentSkillGap
                        .recommendations
                        .map(
                          (
                            recommendation,
                            index,
                          ) => (
                            <li
                              key={`${index}-${String(
                                recommendation,
                              )}`}
                            >
                              {String(
                                recommendation,
                              )}
                            </li>
                          ),
                        )}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              <>
                <p className="jobs-muted">
                  Skill Gap Analysis has not
                  been generated yet.
                </p>

                {skillGapError && (
                  <div className="jobs-info-message">
                    {skillGapError}
                  </div>
                )}

                <Button
                  disabled={
                    skillGapLoading
                  }
                  onClick={
                    handleSkillGapAnalysis
                  }
                >
                  {skillGapLoading
                    ? "Analyzing..."
                    : "Analyze skill gap"}
                </Button>
              </>
            )}
          </Card>

          {/* COVER LETTER */}

          <Card className="application-detail-card">
            <p className="eyebrow">
              Cover letter
            </p>

            <h2>
              Your submission
            </h2>

            <p className="application-cover-letter">
              {application.cover_letter ||
                "No cover letter was submitted."}
            </p>
          </Card>
        </div>

        {/* SIDEBAR */}

        <aside className="application-details-sidebar">

          {/* RESUME */}

          <Card className="application-detail-card">
            <p className="eyebrow">
              Submitted with
            </p>

            <h2>
              Resume
            </h2>

            {resume ? (
              <div className="application-resume-card">
                <div className="resume-file-icon">
                  PDF
                </div>

                <div>
                  <strong>
                    {resume.file_name}
                  </strong>

                  {resume.is_primary && (
                    <span>
                      Default resume
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <p className="jobs-muted">
                No resume attached.
              </p>
            )}
          </Card>

          {/* INTERVIEWS */}

          {workspace.interviews?.length >
            0 && (
            <Card className="application-detail-card">
              <p className="eyebrow">
                Interviews
              </p>

              <h2>
                Interview activity
              </h2>

              <div className="application-interview-list">
                {workspace.interviews.map(
                  (interview) => (
                    <div
                      key={interview.id}
                      className="application-interview"
                    >
                      <strong>
                        {interview.interview_type}
                      </strong>

                      <span>
                        {interview.scheduled_at
                          ? new Date(
                              interview.scheduled_at,
                            ).toLocaleString()
                          : "Not scheduled"}
                      </span>

                      <span>
                        {interview.status}
                      </span>

                      {interview.preparation && (
                        <span>
                          Interview preparation
                          available
                        </span>
                      )}
                    </div>
                  ),
                )}
              </div>
            </Card>
          )}
        </aside>
      </div>
    </section>
  );
}
