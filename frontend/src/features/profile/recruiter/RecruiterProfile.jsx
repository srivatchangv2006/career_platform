import { useState } from "react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import ProfileHeader from "../shared/ProfileHeader";
import ProfileAbout from "../shared/ProfileAbout";
import CreateRecruiterProfile from "./CreateRecruiterProfile";

import {
  updateRecruiterProfile,
} from "../../../api/profile.api";

import { useAuth } from "../../../hooks/useAuth";
import { useProfile } from "../../../hooks/useProfile";

export default function RecruiterProfile() {
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
      company_id:
        profile?.company_id || "",
      designation:
        profile?.designation || "",
      bio:
        profile?.bio || "",
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
      await updateRecruiterProfile({
        company_id:
          form.company_id,
        designation:
          form.designation || null,
        bio:
          form.bio || null,
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
        Loading recruiter profile...
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
      <CreateRecruiterProfile />
    );
  }

  if (!profile) {
    return null;
  }

  const profileForHeader = {
    ...profile,
    headline:
      profile.designation,
  };

  return (
    <section className="profile-page">
      <ProfileHeader
        profile={profileForHeader}
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
                Recruiter settings
              </p>

              <h2>
                Edit recruiter profile
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
              Company ID

              <input
                name="company_id"
                value={form.company_id}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              Designation

              <input
                name="designation"
                value={form.designation}
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
          Recruiter information
        </h2>

        <div className="profile-detail-grid">
          <div>
            <span>
              Designation
            </span>

            <strong>
              {profile.designation ||
                "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Company
            </span>

            <strong>
              Company ID:{" "}
              {profile.company_id}
            </strong>
          </div>
        </div>
      </Card>
    </section>
  );
}
