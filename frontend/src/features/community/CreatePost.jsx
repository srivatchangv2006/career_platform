import {
  useRef,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  createCommunityPost,
} from "../../api/community.api";

export default function CreatePost({
  onCreated,
}) {
  const [title, setTitle] =
    useState("");

  const [content, setContent] =
    useState("");

  const [files, setFiles] =
    useState([]);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const fileInputRef =
    useRef(null);

  function handleFilesChange(event) {
    const selected = Array.from(
      event.target.files || [],
    );

    if (selected.length > 5) {
      setError(
        "You can attach a maximum of 5 images.",
      );

      setFiles(
        selected.slice(0, 5),
      );

      return;
    }

    setError("");
    setFiles(selected);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedTitle =
      title.trim();

    const trimmedContent =
      content.trim();

    if (!trimmedTitle) {
      setError(
        "Please enter a post title.",
      );

      return;
    }

    if (!trimmedContent) {
      setError(
        "Please enter some content.",
      );

      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const formData =
        new FormData();

      formData.append(
        "title",
        trimmedTitle,
      );

      formData.append(
        "content",
        trimmedContent,
      );

      files.forEach(
        (file, index) => {
          formData.append(
            `image${index + 1}`,
            file,
          );
        },
      );

      const post =
        await createCommunityPost(
          formData,
        );

      setTitle("");
      setContent("");
      setFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value =
          "";
      }

      onCreated(post);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create the post.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="community-create-card">
      <div className="community-create-header">
        <div>
          <p className="eyebrow">
            Community
          </p>

          <h2>
            Create a post
          </h2>

          <p>
            Share something useful with
            the MEDAI community.
          </p>
        </div>
      </div>

      {error && (
        <div className="community-message">
          {error}
        </div>
      )}

      <form
        className="community-create-form"
        onSubmit={handleSubmit}
      >
        <label>
          Title

          <input
            type="text"
            value={title}
            onChange={(event) =>
              setTitle(
                event.target.value,
              )
            }
            placeholder="What would you like to discuss?"
            maxLength={200}
            required
          />
        </label>

        <label>
          Content

          <textarea
            rows="6"
            value={content}
            onChange={(event) =>
              setContent(
                event.target.value,
              )
            }
            placeholder="Write your post..."
            required
          />
        </label>

        <label>
          Images

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            onChange={
              handleFilesChange
            }
          />
        </label>

        {files.length > 0 && (
          <div className="community-selected-files">
            {files.map((file) => (
              <span key={file.name}>
                {file.name}
              </span>
            ))}
          </div>
        )}

        <div className="community-create-actions">
          <span>
            {files.length} / 5 images
          </span>

          <Button
            type="submit"
            disabled={submitting}
          >
            {submitting
              ? "Posting..."
              : "Publish post"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
