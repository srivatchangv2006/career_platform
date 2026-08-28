import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Button from "../../../components/ui/Button";

import {
  createApplication,
} from "../../../api/applications.api";

import {
  getMyResumes,
} from "../../../api/resumes.api";

export default function ApplyForm({
  jobId,
  onApplied,
}) {
  const [resumes, setResumes] =
    useState([]);

  const [selectedResumeId, setSelectedResumeId] =
    useState("");

  const [coverLetter, setCoverLetter] =
    useState("");

  const [loadingResumes, setLoadingResumes] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [aiMessage, setAiMessage] =
    useState("");

  const loadResumes =
    useCallback(async () => {
      setLoadingResumes(true);
      setError("");

      try {
        const result =
          await getMyResumes();

        const availableResumes =
          Array.isArray(result)
            ? result
            : [];

        setResumes(
          availableResumes,
        );

        const primaryResume =
          availableResumes.find(
            (resume) =>
              resume.is_primary,
          );

        if (primaryResume) {
          setSelectedResumeId(
            primaryResume.id,
          );
        } else if (
          availableResumes.length > 0
        ) {
          setSelectedResumeId(
            availableResumes[0].id,
          );
        }
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your resumes.",
        );
      } finally {
        setLoadingResumes(false);
      }
    }, []);

  useEffect(() => {
    // Load the candidate's available resumes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadResumes();
  }, [loadResumes]);

  async function handleSubmit(event) {
    event.preventDefault();

    setSubmitting(true);
    setError("");

    try {
      const application =
        await createApplication({
          job_id: jobId,
          resume_id:
            selectedResumeId || null,
          cover_letter:
            coverLetter.trim() || null,
        });

      if (
        application?.ai_analysis_status ===
        "RATE_LIMITED"
      ) {
        setAiMessage(
          "Application submitted successfully. MEDAI Skill Gap Analysis is temporarily unavailable because the AI usage limit has been reached. You can analyze the skill gap later.",
        );
      } else if (
        application?.ai_analysis_status ===
        "UNAVAILABLE"
      ) {
        setAiMessage(
          "Application submitted successfully. MEDAI Skill Gap Analysis is temporarily unavailable. You can analyze the skill gap later.",
        );
      }

      onApplied(application);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to submit your application.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className="job-apply-form"
      onSubmit={handleSubmit}
    >
      <div className="job-apply-form-header">
        <p className="eyebrow">
          Apply
        </p>

        <h2>
          Submit your application
        </h2>

        <p>
          Choose one of your saved resumes
          and optionally add a cover letter.
        </p>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      {aiMessage && (
        <div className="jobs-info-message">
          {aiMessage}
        </div>
      )}

      <label>
        Resume

        {loadingResumes ? (
          <div className="resume-selector-loading">
            Loading your resumes...
          </div>
        ) : resumes.length === 0 ? (
          <div className="resume-selector-empty">
            <p>
              You don't have a resume yet.
              Add one from your profile before
              applying.
            </p>
          </div>
        ) : (
          <select
            value={selectedResumeId}
            onChange={(event) =>
              setSelectedResumeId(
                event.target.value,
              )
            }
            required
          >
            {resumes.map((resume) => (
              <option
                key={resume.id}
                value={resume.id}
              >
                {resume.file_name}
                {resume.is_primary
                  ? " — Default"
                  : ""}
              </option>
            ))}
          </select>
        )}
      </label>

      <label>
        Cover letter

        <textarea
          rows="7"
          value={coverLetter}
          onChange={(event) =>
            setCoverLetter(
              event.target.value,
            )
          }
          placeholder="Tell the recruiter why you're a good fit..."
        />
      </label>

      {resumes.length === 0 &&
        !loadingResumes && (
          <p className="jobs-muted">
            Upload a resume from your candidate
            profile to apply for jobs.
          </p>
        )}

      <Button
        type="submit"
        disabled={
          submitting ||
          loadingResumes ||
          resumes.length === 0 ||
          !selectedResumeId
        }
      >
        {submitting
          ? "Submitting..."
          : "Submit application"}
      </Button>
    </form>
  );
}
