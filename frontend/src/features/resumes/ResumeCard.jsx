import { useState } from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

export default function ResumeCard({
  resume,
  onSetPrimary,
  onRename,
  onDelete,
  actionLoading,
}) {
  const [renaming, setRenaming] =
    useState(false);

  const [name, setName] =
    useState(resume.file_name || "");

  function handleRename(event) {
    event.preventDefault();

    const trimmedName =
      name.trim();

    if (!trimmedName) {
      return;
    }

    onRename(
      resume.id,
      trimmedName,
    );

    setRenaming(false);
  }

  const uploadedDate =
    resume.created_at
      ? new Date(
          resume.created_at,
        ).toLocaleDateString()
      : "";

  return (
    <Card className="resume-card">
      <div className="resume-card-main">
        <div className="resume-file-icon">
          PDF
        </div>

        <div className="resume-card-info">
          {!renaming ? (
            <div className="resume-title-row">
              <h3>
                {resume.file_name}
              </h3>

              {resume.is_primary && (
                <span className="resume-default-badge">
                  Default
                </span>
              )}
            </div>
          ) : (
            <form
              className="resume-rename-form"
              onSubmit={handleRename}
            >
              <input
                type="text"
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value,
                  )
                }
                maxLength={200}
                autoFocus
              />

              <div className="resume-inline-actions">
                <Button
                  type="submit"
                  disabled={
                    actionLoading
                  }
                >
                  Save
                </Button>

                <Button
                  type="button"
                  variant="ghost"
                  onClick={() =>
                    setRenaming(false)
                  }
                  disabled={
                    actionLoading
                  }
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          <p className="resume-meta">
            PDF
            {resume.file_size_bytes
              ? ` · ${(
                  resume.file_size_bytes /
                  1024 /
                  1024
                ).toFixed(2)} MB`
              : ""}
            {uploadedDate
              ? ` · Uploaded ${uploadedDate}`
              : ""}
          </p>
        </div>
      </div>

      {!renaming && (
        <div className="resume-card-actions">
          {!resume.is_primary && (
            <Button
              variant="secondary"
              disabled={actionLoading}
              onClick={() =>
                onSetPrimary(
                  resume.id,
                )
              }
            >
              Set default
            </Button>
          )}

          <Button
            variant="ghost"
            disabled={actionLoading}
            onClick={() =>
              setRenaming(true)
            }
          >
            Rename
          </Button>

          <Button
            variant="ghost"
            disabled={actionLoading}
            onClick={() =>
              onDelete(resume.id)
            }
          >
            Delete
          </Button>
        </div>
      )}
    </Card>
  );
}
