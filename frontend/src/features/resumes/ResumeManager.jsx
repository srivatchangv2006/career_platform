import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";

import {
  getMyResumes,
  setPrimaryResume,
  renameResume,
  deleteResume,
} from "../../api/resumes.api";

import ResumeCard from "./ResumeCard";
import UploadResumeForm from "./UploadResumeForm";

export default function ResumeManager() {
  const [resumes, setResumes] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [actionLoading, setActionLoading] =
    useState(false);

  const [aiMessage, setAiMessage] =
    useState("");

  const loadResumes =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const result =
          await getMyResumes();

        setResumes(
          Array.isArray(result)
            ? result
            : [],
        );
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your resumes.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Load candidate resumes when the manager mounts.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadResumes();
  }, [loadResumes]);

  async function handleUploaded(
    resume,
  ) {
    if (
      resume?.ai_analysis_status ===
      "RATE_LIMITED"
    ) {
      setAiMessage(
        "Resume uploaded successfully. MEDAI analysis is temporarily unavailable because the AI usage limit has been reached. You can continue using MEDAI and analyze it later.",
      );
    } else if (
      resume?.ai_analysis_status ===
      "UNAVAILABLE"
    ) {
      setAiMessage(
        "Resume uploaded successfully. MEDAI analysis is temporarily unavailable. You can try the analysis again later.",
      );
    } else if (
      resume?.ai_analysis_status ===
      "COMPLETED"
    ) {
      setAiMessage(
        "Resume uploaded and MEDAI analysis completed.",
      );
    }

    setResumes((current) => {
      const withoutDuplicate =
        current.filter(
          (item) =>
            item.id !== resume.id,
        );

      return [
        ...withoutDuplicate,
        resume,
      ].sort(
        (a, b) =>
          Number(b.is_primary) -
            Number(a.is_primary) ||
          new Date(
            b.created_at,
          ) -
            new Date(
              a.created_at,
            ),
      );
    });
  }

  async function handleSetPrimary(
    resumeId,
  ) {
    setActionLoading(true);
    setError("");

    try {
      const updated =
        await setPrimaryResume(
          resumeId,
        );

      setResumes((current) =>
        current.map((resume) => ({
          ...resume,
          is_primary:
            resume.id === updated.id,
        })),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to change the default resume.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRename(
    resumeId,
    name,
  ) {
    setActionLoading(true);
    setError("");

    try {
      const updated =
        await renameResume(
          resumeId,
          name,
        );

      setResumes((current) =>
        current.map((resume) =>
          resume.id === updated.id
            ? updated
            : resume,
        ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to rename the resume.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDelete(
    resumeId,
  ) {
    const confirmed =
      window.confirm(
        "Delete this resume? This cannot be undone.",
      );

    if (!confirmed) {
      return;
    }

    setActionLoading(true);
    setError("");

    try {
      await deleteResume(
        resumeId,
      );

      setResumes((current) =>
        current.filter(
          (resume) =>
            resume.id !== resumeId,
        ),
      );

      // Reload so default-promotion is reflected immediately.
      await loadResumes();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to delete the resume.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  return (
    <Card className="profile-section-card resume-manager">
      <div className="resume-manager-header">
        <div>
          <p className="eyebrow">
            Career documents
          </p>

          <h2>
            My resumes
          </h2>

          <p className="resume-manager-description">
            Keep up to 3 resumes ready for
            different opportunities. Your
            default resume can be used as
            your preferred application resume.
          </p>
        </div>

        <span className="resume-count-badge">
          {resumes.length} / 3
        </span>
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

      {loading && (
        <p className="network-muted">
          Loading your resumes...
        </p>
      )}

      {!loading &&
        resumes.length === 0 && (
          <div className="resume-empty-state">
            <h3>
              No resumes uploaded
            </h3>

            <p>
              Upload your first resume so
              you can quickly use it when
              applying for jobs.
            </p>
          </div>
        )}

      {!loading &&
        resumes.length > 0 && (
          <div className="resume-list">
            {resumes.map((resume) => (
              <ResumeCard
                key={resume.id}
                resume={resume}
                onSetPrimary={
                  handleSetPrimary
                }
                onRename={
                  handleRename
                }
                onDelete={
                  handleDelete
                }
                actionLoading={
                  actionLoading
                }
              />
            ))}
          </div>
        )}

      <UploadResumeForm
        currentCount={resumes.length}
        onUploaded={
          handleUploaded
        }
      />
    </Card>
  );
}
