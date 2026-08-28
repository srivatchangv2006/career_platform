import { useState } from "react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import { createProfile } from "../../../api/profiles.api";

import { useAuth } from "../../../hooks/useAuth";
import { useProfile } from "../../../hooks/useProfile";

export default function CreateCandidateProfile() {
  const { user } = useAuth();
  const { refreshProfile } =
    useProfile();

  const [form, setForm] = useState({
    full_name:
      user?.email?.split("@")[0] || "",
    headline: "",
    bio: "",
    location: "",
    years_of_experience: "",
    profile_image_blob_path: "",
  });

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  function handleChange(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]:
        event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setError("");

    try {
      await createProfile({
        full_name:
          form.full_name.trim(),
        headline:
          form.headline.trim() || null,
        bio:
          form.bio.trim() || null,
        location:
          form.location.trim() || null,
        years_of_experience:
          form.years_of_experience === ""
            ? null
            : Number(
                form.years_of_experience,
              ),
        profile_image_blob_path:
          form.profile_image_blob_path
            .trim() || null,
      });

      await refreshProfile();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create your profile.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="profile-setup-page">
      <Card className="profile-setup-card">
        <div className="profile-setup-header">
          <p className="eyebrow">
            Welcome to MEDAI
          </p>

          <h1>
            Complete your profile
          </h1>

          <p>
            Add a few details so people can
            understand who you are and what
            you do.
          </p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form
          className="profile-form"
          onSubmit={handleSubmit}
        >
          <label>
            Full name

            <input
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              placeholder="Your full name"
              required
            />
          </label>

          <label>
            Professional headline

            <input
              name="headline"
              value={form.headline}
              onChange={handleChange}
              placeholder="Backend Developer"
            />
          </label>

          <label>
            Location

            <input
              name="location"
              value={form.location}
              onChange={handleChange}
              placeholder="Chennai"
            />
          </label>

          <label>
            Years of experience

            <input
              name="years_of_experience"
              type="number"
              min="0"
              step="0.1"
              value={
                form.years_of_experience
              }
              onChange={handleChange}
              placeholder="0"
            />
          </label>

          <label>
            About you

            <textarea
              name="bio"
              rows="6"
              value={form.bio}
              onChange={handleChange}
              placeholder="Tell the MEDAI community about yourself..."
            />
          </label>

          <label>
            Profile image blob path

            <input
              name="profile_image_blob_path"
              value={
                form.profile_image_blob_path
              }
              onChange={handleChange}
              placeholder="Optional"
            />
          </label>

          <Button
            type="submit"
            disabled={saving}
          >
            {saving
              ? "Creating profile..."
              : "Create Profile"}
          </Button>
        </form>
      </Card>
    </section>
  );
}
