import { useRef, useState } from "react";

import Button from "../../components/ui/Button";

import {
  uploadResume,
} from "../../api/resumes.api";

export default function UploadResumeForm({
  currentCount,
  onUploaded,
}) {
  const [resumeName, setResumeName] =
    useState("");

  const [file, setFile] =
    useState(null);

  const [uploading, setUploading] =
    useState(false);

  const [error, setError] =
    useState("");

  const fileInputRef =
    useRef(null);

  const maxReached =
    currentCount >= 3;

  function handleFileChange(event) {
    const selectedFile =
      event.target.files?.[0] ||
      null;

    setFile(selectedFile);
    setError("");

    if (
      selectedFile &&
      !resumeName.trim()
    ) {
      setResumeName(
        selectedFile.name.replace(
          /\.pdf$/i,
          "",
        ),
      );
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (maxReached) {
      return;
    }

    if (!file) {
      setError(
        "Please choose a PDF resume.",
      );
      return;
    }

    if (
      file.type !==
      "application/pdf"
    ) {
      setError(
        "Only PDF resumes are allowed.",
      );
      return;
    }

    setUploading(true);
    setError("");

    try {
      const resume =
        await uploadResume(
          file,
          resumeName,
        );

      setResumeName("");
      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value =
          "";
      }

      onUploaded(resume);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to upload resume.",
      );
    } finally {
      setUploading(false);
    }
  }

  if (maxReached) {
    return (
      <div className="resume-upload-limit">
        You have reached the maximum of
        3 resumes.
      </div>
    );
  }

  return (
    <form
      className="resume-upload-form"
      onSubmit={handleSubmit}
    >
      <div className="resume-upload-header">
        <div>
          <p className="eyebrow">
            Add a resume
          </p>

          <h3>
            Upload another resume
          </h3>
        </div>

        <span className="resume-count">
          {currentCount} / 3
        </span>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <label>
        Resume name

        <input
          type="text"
          value={resumeName}
          onChange={(event) =>
            setResumeName(
              event.target.value,
            )
          }
          placeholder="e.g. Backend Engineer Resume"
          maxLength={200}
        />
      </label>

      <label>
        PDF file

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
        />
      </label>

      {file && (
        <p className="resume-selected-file">
          Selected: {file.name}
        </p>
      )}

      <Button
        type="submit"
        disabled={
          uploading ||
          !file
        }
      >
        {uploading
          ? "Uploading..."
          : "Upload resume"}
      </Button>
    </form>
  );
}
