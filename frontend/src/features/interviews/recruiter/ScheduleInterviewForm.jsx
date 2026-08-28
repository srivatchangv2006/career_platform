import {
  useState,
} from "react";

import Button from "../../../components/ui/Button";

import {
  createRecruiterInterview,
  updateRecruiterInterview,
} from "../../../api/recruiterInterviews.api";


function toDateTimeLocal(value) {
  if (!value) {
    return "";
  }

  const date =
    new Date(value);

  const offset =
    date.getTimezoneOffset();

  const local =
    new Date(
      date.getTime()
      - offset * 60000,
    );

  return local
    .toISOString()
    .slice(0, 16);
}


export default function ScheduleInterviewForm({
  applicationId,
  initialInterview = null,
  onCreated,
  onUpdated,
  onCancel,
}) {
  const editing =
    Boolean(initialInterview);

  const [form, setForm] =
    useState({
      interview_type:
        initialInterview?.interview_type ||
        "TECHNICAL",

      scheduled_at:
        toDateTimeLocal(
          initialInterview?.scheduled_at,
        ),

      duration_minutes:
        initialInterview?.duration_minutes
          ?.toString() ||
        "60",

      meeting_url:
        initialInterview?.meeting_url ||
        "",

      location:
        initialInterview?.location ||
        "",

      notes:
        initialInterview?.notes ||
        "",

      status:
        initialInterview?.status ||
        "SCHEDULED",
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

    if (!form.interview_type.trim()) {
      setError(
        "Please select an interview type.",
      );
      return;
    }

    if (!form.scheduled_at) {
      setError(
        "Please choose the interview date and time.",
      );
      return;
    }

    setSaving(true);
    setError("");

    const payload = {
      interview_type:
        form.interview_type,

      scheduled_at:
        new Date(
          form.scheduled_at,
        ).toISOString(),

      duration_minutes:
        form.duration_minutes === ""
          ? null
          : Number(
              form.duration_minutes,
            ),

      meeting_url:
        form.meeting_url.trim() ||
        null,

      location:
        form.location.trim() ||
        null,

      notes:
        form.notes.trim() ||
        null,

      status:
        form.status,
    };

    try {
      if (editing) {
        const updated =
          await updateRecruiterInterview(
            initialInterview.id,
            payload,
          );

        onUpdated(updated);
      } else {
        const created =
          await createRecruiterInterview({
            application_id:
              applicationId,
            ...payload,
          });

        onCreated(created);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          (
            editing
              ? "Unable to update the interview."
              : "Unable to schedule the interview."
          ),
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      className="schedule-interview-form"
      onSubmit={handleSubmit}
    >
      <div className="schedule-interview-header">
        <div>
          <p className="eyebrow">
            Interview
          </p>

          <h3>
            {editing
              ? "Edit interview"
              : "Schedule interview"}
          </h3>

          <p>
            {editing
              ? "Update the appointment details for the candidate."
              : "Send the candidate a structured interview appointment."}
          </p>
        </div>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <div className="schedule-interview-grid">
        <label>
          Interview type

          <select
            name="interview_type"
            value={
              form.interview_type
            }
            onChange={
              handleChange
            }
          >
            <option value="TECHNICAL">
              Technical
            </option>

            <option value="HR">
              HR
            </option>

            <option value="BEHAVIORAL">
              Behavioral
            </option>

            <option value="MANAGERIAL">
              Managerial
            </option>

            <option value="FINAL">
              Final
            </option>
          </select>
        </label>

        <label>
          Date and time

          <input
            type="datetime-local"
            name="scheduled_at"
            value={
              form.scheduled_at
            }
            onChange={
              handleChange
            }
            required
          />
        </label>

        <label>
          Duration

          <input
            type="number"
            name="duration_minutes"
            min="1"
            value={
              form.duration_minutes
            }
            onChange={
              handleChange
            }
          />
        </label>

        <label>
          Meeting URL

          <input
            type="url"
            name="meeting_url"
            value={
              form.meeting_url
            }
            onChange={
              handleChange
            }
            placeholder="https://meet.example.com/..."
          />
        </label>

        <label>
          Location

          <input
            type="text"
            name="location"
            value={
              form.location
            }
            onChange={
              handleChange
            }
            placeholder="Online / Chennai office"
          />
        </label>

        <label>
          Status

          <select
            name="status"
            value={
              form.status
            }
            onChange={
              handleChange
            }
          >
            <option value="SCHEDULED">
              Scheduled
            </option>

            <option value="CONFIRMED">
              Confirmed
            </option>

            <option value="COMPLETED">
              Completed
            </option>

            <option value="RESCHEDULED">
              Rescheduled
            </option>
          </select>
        </label>
      </div>

      <label>
        Notes

        <textarea
          name="notes"
          rows="5"
          value={
            form.notes
          }
          onChange={
            handleChange
          }
          placeholder="Instructions or information for the candidate..."
        />
      </label>

      <div className="schedule-interview-actions">
        <Button
          type="button"
          variant="ghost"
          onClick={
            onCancel
          }
          disabled={saving}
        >
          Cancel
        </Button>

        <Button
          type="submit"
          disabled={saving}
        >
          {saving
            ? (
              editing
                ? "Saving..."
                : "Scheduling..."
            )
            : (
              editing
                ? "Save changes"
                : "Schedule interview"
            )}
        </Button>
      </div>
    </form>
  );
}
