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
import ScheduleInterviewForm from "../../features/interviews/recruiter/ScheduleInterviewForm";
import {
  getRecruiterApplicationDetails,
  getRecruiterApplicationAnswers,
  updateRecruiterApplicationStatus,
  downloadRecruiterResume,
} from "../../api/recruiterApplications.api";

import {
  getRecruiterInterviews,
  updateRecruiterInterview,
  deleteRecruiterInterview,
} from "../../api/recruiterInterviews.api";

export default function ApplicantDetailsPage() {
  const { applicationId } =
    useParams();

  const [data, setData] =
    useState(null);

  const [answers, setAnswers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [updating, setUpdating] =
    useState(false);

  const [downloadingResume, setDownloadingResume] =
    useState(false);

  const [resumeError, setResumeError] =
    useState("");

  const [interviews, setInterviews] =
    useState([]);

  const [showScheduleForm, setShowScheduleForm] =
    useState(false);

  const [editingInterview, setEditingInterview] =
    useState(null);

  const [interviewActionError, setInterviewActionError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function loadDetails() {
      setLoading(true);
      setError("");

      try {
        const [
          details,
          screeningAnswers,
          recruiterInterviews,
        ] = await Promise.all([
          getRecruiterApplicationDetails(
            applicationId,
          ),
          getRecruiterApplicationAnswers(
            applicationId,
          ),
          getRecruiterInterviews(),
        ]);

        if (!active) {
          return;
        }

        setData(details);

        setAnswers(
          Array.isArray(
            screeningAnswers,
          )
            ? screeningAnswers
            : [],
        );

        setInterviews(
          Array.isArray(
            recruiterInterviews,
          )
            ? recruiterInterviews.filter(
                (interview) =>
                  String(
                    interview.application_id,
                  ) ===
                  String(
                    applicationId,
                  ),
              )
            : [],
        );
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load applicant details.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDetails();

    return () => {
      active = false;
    };
  }, [applicationId]);

  function handleInterviewCreated(
    interview,
  ) {
    setInterviews((current) => [
      ...current,
      interview,
    ]);

    setShowScheduleForm(false);
  }

  function handleInterviewUpdated(
    updatedInterview,
  ) {
    setInterviews(
      (current) =>
        current.map(
          (interview) =>
            interview.id ===
            updatedInterview.id
              ? updatedInterview
              : interview,
        ),
    );

    setEditingInterview(null);
    setInterviewActionError("");
  }

  async function handleCancelInterview(
    interviewId,
  ) {
    const confirmed =
      window.confirm(
        "Cancel this interview?",
      );

    if (!confirmed) {
      return;
    }

    setInterviewActionError("");

    try {
      const updated =
        await updateRecruiterInterview(
          interviewId,
          {
            status: "CANCELLED",
          },
        );

      setInterviews(
        (current) =>
          current.map(
            (interview) =>
              interview.id ===
              interviewId
                ? updated
                : interview,
          ),
      );
    } catch (err) {
      setInterviewActionError(
        err?.response?.data?.detail ||
          "Unable to cancel the interview.",
      );
    }
  }

  async function handleDeleteInterview(
    interviewId,
  ) {
    const confirmed =
      window.confirm(
        "Delete this interview permanently?",
      );

    if (!confirmed) {
      return;
    }

    setInterviewActionError("");

    try {
      await deleteRecruiterInterview(
        interviewId,
      );

      setInterviews(
        (current) =>
          current.filter(
            (interview) =>
              interview.id !==
              interviewId,
          ),
      );
    } catch (err) {
      setInterviewActionError(
        err?.response?.data?.detail ||
          "Unable to delete the interview.",
      );
    }
  }

  async function handleResumeDownload() {
    if (!resume?.id) {
      return;
    }

    setDownloadingResume(true);
    setResumeError("");

    try {
      const result =
        await downloadRecruiterResume(
          applicationId,
        );

      const url =
        URL.createObjectURL(
          result.blob,
        );

      const link =
        document.createElement("a");

      link.href = url;

      const filename =
        resume.file_name ||
        "candidate-resume.pdf";

      link.download = filename;

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);
    } catch (err) {
      setResumeError(
        err?.response?.data?.detail ||
          "Unable to download the resume.",
      );
    } finally {
      setDownloadingResume(false);
    }
  }

  async function handleStatusChange(
    event,
  ) {
    const nextStatus =
      event.target.value;

    setUpdating(true);
    setError("");

    try {
      const updated =
        await updateRecruiterApplicationStatus(
          applicationId,
          {
            status: nextStatus,
          },
        );

      setData((current) => ({
        ...current,
        application: {
          ...current.application,
          status:
            updated.status,
          updated_at:
            updated.updated_at,
        },
      }));
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update application status.",
      );
    } finally {
      setUpdating(false);
    }
  }

  if (loading) {
    return (
      <Card className="feed-state">
        Loading applicant...
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card className="feed-state feed-error">
        {error ||
          "Applicant not found."}
      </Card>
    );
  }

  const candidate =
    data.candidate;

  const profile =
    candidate.profile;

  const job = data.job;

  const application =
    data.application;

  const resume =
    data.resume;

  return (
    <section className="applicant-details-page">
      <Link
        to="/recruiter/applicants"
        className="applicant-back-link"
      >
        ← Back to applicants
      </Link>

      <Card className="applicant-details-hero">
        <div className="applicant-details-identity">
          <div className="applicant-large-avatar">
            {(profile?.full_name ||
              candidate.email ||
              "C")
              .charAt(0)
              .toUpperCase()}
          </div>

          <div>
            <p className="eyebrow">
              Candidate
            </p>

            <h1>
              {profile?.full_name ||
                candidate.email}
            </h1>

            <p className="applicant-email">
              {candidate.email}
            </p>

            {profile?.headline && (
              <p className="applicant-headline">
                {profile.headline}
              </p>
            )}
          </div>
        </div>

        <div className="applicant-details-status">
          <span className="eyebrow">
            Application status
          </span>

          <select
            value={
              application.status
            }
            disabled={updating}
            onChange={
              handleStatusChange
            }
          >
            <option
              value={
                application.status
              }
            >
              {application.status}
            </option>

            {application.status ===
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

            {application.status ===
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

            {application.status ===
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

            {application.status ===
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

            {application.status ===
              "OFFER" && (
              <option value="REJECTED">
                Rejected
              </option>
            )}
          </select>
        </div>
      </Card>

      <div className="applicant-details-grid">
        <div className="applicant-details-main">

          {/* JOB */}

          <Card className="applicant-details-card">
            <p className="eyebrow">
              Applied for
            </p>

            <h2>
              {job.title}
            </h2>

            <p className="applicant-job-company">
              {job.company_name ||
                "Company"}
            </p>

            <div className="applicant-job-meta">
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
          </Card>

          {/* PROFILE */}

          <Card className="applicant-details-card">
            <p className="eyebrow">
              Candidate profile
            </p>

            <h2>
              About the candidate
            </h2>

            {profile?.bio ? (
              <p className="applicant-bio">
                {profile.bio}
              </p>
            ) : (
              <p className="jobs-muted">
                No bio provided.
              </p>
            )}

            <div className="applicant-profile-grid">
              <div>
                <span>
                  Location
                </span>

                <strong>
                  {profile?.location ||
                    "Not specified"}
                </strong>
              </div>

              <div>
                <span>
                  Experience
                </span>

                <strong>
                  {profile?.years_of_experience ??
                    0}{" "}
                  years
                </strong>
              </div>
            </div>
          </Card>

          {/* SKILLS */}

          <Card className="applicant-details-card">
            <p className="eyebrow">
              Skills
            </p>

            <h2>
              Candidate skills
            </h2>

            {candidate.skills?.length >
            0 ? (
              <div className="applicant-skill-list">
                {candidate.skills.map(
                  (skill) => (
                    <span
                      key={skill.skill_id}
                    >
                      {skill.skill_name}
                    </span>
                  ),
                )}
              </div>
            ) : (
              <p className="jobs-muted">
                No skills listed.
              </p>
            )}
          </Card>

          {/* SCREENING ANSWERS */}

          {answers.length > 0 && (
            <Card className="applicant-details-card">
              <p className="eyebrow">
                Screening
              </p>

              <h2>
                Screening answers
              </h2>

              <div className="applicant-answer-list">
                {answers.map(
                  (answer) => (
                    <div
                      key={answer.id}
                      className="applicant-answer"
                    >
                      <h3>
                        {answer.question}
                      </h3>

                      <p>
                        {answer.answer}
                      </p>
                    </div>
                  ),
                )}
              </div>
            </Card>
          )}
        </div>

        <aside className="applicant-details-sidebar">

          {/* INTERVIEWS */}

          <Card className="applicant-details-card">
            <div className="applicant-interview-header">
              <div>
                <p className="eyebrow">
                  Interviews
                </p>

                <h2>
                  Interview scheduling
                </h2>
              </div>

              {!showScheduleForm &&
                !editingInterview && (
                <Button
                  onClick={() => {
                    setInterviewActionError("");
                    setShowScheduleForm(true);
                  }}
                >
                  Schedule interview
                </Button>
              )}
            </div>

            {interviewActionError && (
              <div className="jobs-info-message">
                {interviewActionError}
              </div>
            )}

            {showScheduleForm && (
              <ScheduleInterviewForm
                applicationId={
                  applicationId
                }
                onCreated={
                  handleInterviewCreated
                }
                onCancel={() => {
                  setShowScheduleForm(false);
                  setInterviewActionError("");
                }}
              />
            )}

            {editingInterview && (
              <ScheduleInterviewForm
                applicationId={
                  applicationId
                }
                initialInterview={
                  editingInterview
                }
                onUpdated={
                  handleInterviewUpdated
                }
                onCancel={() => {
                  setEditingInterview(null);
                  setInterviewActionError("");
                }}
              />
            )}

            {!showScheduleForm &&
              !editingInterview &&
              interviews.length === 0 && (
              <p className="jobs-muted">
                No interview has been
                scheduled for this application.
              </p>
            )}

            {!showScheduleForm &&
              !editingInterview &&
              interviews.length > 0 && (
              <div className="recruiter-interview-list">
                {interviews.map(
                  (interview) => (
                    <div
                      key={interview.id}
                      className="recruiter-interview-item"
                    >
                      <div>
                        <strong>
                          {
                            interview.interview_type
                          }
                        </strong>

                        <span>
                          {interview.scheduled_at
                            ? new Date(
                                interview.scheduled_at,
                              ).toLocaleString()
                            : "Not scheduled"}
                        </span>

                        <span>
                          {interview.duration_minutes
                            ? `${interview.duration_minutes} minutes`
                            : "Duration not specified"}
                        </span>

                        {interview.location && (
                          <span>
                            {interview.location}
                          </span>
                        )}
                      </div>

                      <div className="recruiter-interview-actions">
                        <span className="interview-status">
                          {
                            interview.status
                          }
                        </span>

                        {interview.meeting_url && (
                          <a
                            href={
                              interview.meeting_url
                            }
                            target="_blank"
                            rel="noreferrer"
                          >
                            Meeting
                          </a>
                        )}

                        <button
                          type="button"
                          onClick={() => {
                            setShowScheduleForm(false);
                            setInterviewActionError("");
                            setEditingInterview(
                              interview,
                            );
                          }}
                        >
                          Edit
                        </button>

                        {interview.status !==
                          "CANCELLED" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleCancelInterview(
                                interview.id,
                              )
                            }
                          >
                            Cancel
                          </button>
                        )}

                        <button
                          type="button"
                          className="recruiter-interview-delete"
                          onClick={() =>
                            handleDeleteInterview(
                              interview.id,
                            )
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ),
                )}
              </div>
            )}
          </Card>

          {/* RESUME */}

          <Card className="applicant-details-card">
            <p className="eyebrow">
              Application
            </p>

            <h2>
              Resume
            </h2>

            {resume ? (
              <>
                <div className="applicant-resume-box">
                  <strong>
                    {resume.file_name}
                  </strong>

                  {resume.is_primary && (
                    <span>
                      Candidate's default resume
                    </span>
                  )}

                  <p>
                    {resume.content_type}
                    {resume.file_size_bytes
                      ? ` · ${(
                          resume.file_size_bytes /
                          1024 /
                          1024
                        ).toFixed(2)} MB`
                      : ""}
                  </p>
                </div>

                {resumeError && (
                  <div className="jobs-info-message">
                    {resumeError}
                  </div>
                )}

                <button
                  type="button"
                  className="applicant-resume-download"
                  disabled={downloadingResume}
                  onClick={
                    handleResumeDownload
                  }
                >
                  {downloadingResume
                    ? "Downloading..."
                    : "Download resume"}
                </button>
              </>
            ) : (
              <p className="jobs-muted">
                No resume attached.
              </p>
            )}
          </Card>

          {/* APPLICATION */}

          <Card className="applicant-details-card">
            <p className="eyebrow">
              Submission
            </p>

            <h2>
              Cover letter
            </h2>

            <p className="applicant-cover-letter">
              {application.cover_letter ||
                "No cover letter submitted."}
            </p>

            <p className="applicant-applied-date">
              Applied{" "}
              {application.applied_at
                ? new Date(
                    application.applied_at,
                  ).toLocaleString()
                : ""}
            </p>
          </Card>
        </aside>
      </div>
    </section>
  );
}
