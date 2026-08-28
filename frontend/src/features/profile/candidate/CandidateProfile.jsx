import { useState } from "react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import ProfileHeader from "../shared/ProfileHeader";
import ProfileAbout from "../shared/ProfileAbout";
import CreateCandidateProfile from "./CreateCandidateProfile";
import ResumeManager from "../../resumes/ResumeManager";
import {
  updateCandidateProfile,
} from "../../../api/profile.api";

import { useAuth } from "../../../hooks/useAuth";
import { useProfile } from "../../../hooks/useProfile";

export default function CandidateProfile() {
  const { user } = useAuth();

  const {
    profile,
    profileExists,
    loading,
    error,
    refreshProfile,
  } = useProfile();

  const [editing, setEditing] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [form, setForm] =
    useState(null);

  function startEditing() {
    setForm({
      full_name:
        profile?.full_name || "",
      headline:
        profile?.headline || "",
      bio:
        profile?.bio || "",
      location:
        profile?.location || "",
      years_of_experience:
        profile?.years_of_experience ?? "",
      profile_image_blob_path:
        profile?.profile_image_blob_path ||
        "",
    });

    setEditing(true);
  }

  function handleChange(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]:
        event.target.value,
    }));
  }

  async function handleSave(event) {
    event.preventDefault();

    setSaving(true);

    try {
      await updateCandidateProfile({
        ...form,
        years_of_experience:
          form.years_of_experience === ""
            ? null
            : Number(
                form.years_of_experience,
              ),
      });

      await refreshProfile();
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="page-loading">
        Loading profile...
      </div>
    );
  }

  if (error) {
    return (
      <Card className="feed-state feed-error">
        {error}
      </Card>
    );
  }

  if (profileExists === false) {
    return (
      <CreateCandidateProfile />
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <section className="profile-page">
      <ProfileHeader
        profile={profile}
        email={user?.email}
        role={user?.role}
        isOwnProfile
        onEdit={startEditing}
      />

      {editing && (
        <Card className="profile-section-card">
          <div className="profile-edit-header">
            <div>
              <p className="eyebrow">
                Profile settings
              </p>

              <h2>
                Edit your profile
              </h2>
            </div>

            <Button
              variant="ghost"
              onClick={() =>
                setEditing(false)
              }
            >
              Cancel
            </Button>
          </div>

          <form
            className="profile-form"
            onSubmit={handleSave}
          >
            <label>
              Full name

              <input
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              Headline

              <input
                name="headline"
                value={form.headline}
                onChange={handleChange}
              />
            </label>

            <label>
              Location

              <input
                name="location"
                value={form.location}
                onChange={handleChange}
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
              />
            </label>

            <label>
              Bio

              <textarea
                name="bio"
                rows="6"
                value={form.bio}
                onChange={handleChange}
              />
            </label>

            <Button
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : "Save changes"}
            </Button>
          </form>
        </Card>
      )}

      <ProfileAbout
        profile={profile}
      />

      <Card className="profile-section-card">
        <h2>
          Professional information
        </h2>

        <div className="profile-detail-grid">
          <div>
            <span>
              Location
            </span>

            <strong>
              {profile.location ||
                "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Experience
            </span>

            <strong>
              {profile.years_of_experience ??
                0}{" "}
              years
            </strong>
          </div>
        </div>
      </Card>
      <ResumeManager />
    </section>
  );
}
