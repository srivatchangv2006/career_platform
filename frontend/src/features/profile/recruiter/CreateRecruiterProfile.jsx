import { useState } from "react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import {
  createRecruiterProfile,
} from "../../../api/recruiterProfiles.api";

import { useProfile } from "../../../hooks/useProfile";

export default function CreateRecruiterProfile() {
  const { refreshProfile } =
    useProfile();

  const [form, setForm] = useState({
    company_id: "",
    designation: "",
    bio: "",
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
      await createRecruiterProfile({
        company_id:
          form.company_id.trim(),
        designation:
          form.designation.trim() || null,
        bio:
          form.bio.trim() || null,
      });

      await refreshProfile();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create your recruiter profile.",
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
            Complete your recruiter profile
          </h1>

          <p>
            Add your recruiter details so
            candidates can understand your
            role and company.
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
            Company ID

            <input
              name="company_id"
              value={form.company_id}
              onChange={handleChange}
              placeholder="Company UUID"
              required
            />
          </label>

          <label>
            Designation

            <input
              name="designation"
              value={form.designation}
              onChange={handleChange}
              placeholder="Technical Recruiter"
            />
          </label>

          <label>
            About you

            <textarea
              name="bio"
              rows="6"
              value={form.bio}
              onChange={handleChange}
              placeholder="Tell candidates about your recruiting role..."
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
