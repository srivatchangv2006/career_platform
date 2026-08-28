import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import {
  getMyJobs,
  createJob,
  updateJob,
} from "../../../api/jobs.api";

import {
  getCompanies,
} from "../../../api/companies.api";

import {
  getSkills,
  getJobSkills,
  addJobSkill,
  deleteJobSkill,
} from "../../../api/skills.api";

export default function RecruiterJobs() {
  const [jobs, setJobs] =
    useState([]);

  const [companies, setCompanies] =
    useState([]);

  const [skills, setSkills] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [editingJobId, setEditingJobId] =
    useState(null);

  const [saving, setSaving] =
    useState(false);

  const [loadingJobSkills, setLoadingJobSkills] =
    useState(false);

  const emptyForm = {
    company_id: "",
    title: "",
    description: "",
    location: "",
    employment_type: "",
    experience_level: "",
    salary_min: "",
    salary_max: "",
    currency: "USD",
    application_deadline: "",
    status: "DRAFT",
    skill_ids: [],
  };

  const [form, setForm] =
    useState(emptyForm);

  const loadJobs =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const [
          jobsResult,
          companiesResult,
          skillsResult,
        ] = await Promise.all([
          getMyJobs(),
          getCompanies(),
          getSkills(),
        ]);

        setJobs(
          Array.isArray(jobsResult)
            ? jobsResult
            : [],
        );

        setCompanies(
          Array.isArray(
            companiesResult,
          )
            ? companiesResult
            : [],
        );

        setSkills(
          Array.isArray(skillsResult)
            ? skillsResult
            : [],
        );
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load recruiter data.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Load recruiter jobs, companies, and skill catalog.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadJobs();
  }, [loadJobs]);

  async function loadExistingJobSkills(
    jobId,
  ) {
    setLoadingJobSkills(true);

    try {
      const result =
        await getJobSkills(jobId);

      const selectedIds =
        Array.isArray(result)
          ? result.map(
              (jobSkill) =>
                String(
                  jobSkill.skill_id,
                ),
            )
          : [];

      setForm((current) => ({
        ...current,
        skill_ids: selectedIds,
      }));
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to load job skills.",
      );
    } finally {
      setLoadingJobSkills(false);
    }
  }

  function startCreate() {
    setEditingJobId(null);
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  }

  function startEdit(job) {
    setEditingJobId(job.id);

    setForm({
      company_id:
        job.company_id || "",
      title:
        job.title || "",
      description:
        job.description || "",
      location:
        job.location || "",
      employment_type:
        job.employment_type || "",
      experience_level:
        job.experience_level || "",
      salary_min:
        job.salary_min ?? "",
      salary_max:
        job.salary_max ?? "",
      currency:
        job.currency || "USD",
      application_deadline:
        job.application_deadline || "",
      status:
        job.status || "DRAFT",
      skill_ids: [],
    });

    setError("");
    setShowForm(true);

    loadExistingJobSkills(
      job.id,
    );
  }

  function handleChange(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]:
        event.target.value,
    }));
  }

  function toggleSkill(skillId) {
    const id = String(skillId);

    setForm((current) => {
      const alreadySelected =
        current.skill_ids.includes(id);

      return {
        ...current,
        skill_ids: alreadySelected
          ? current.skill_ids.filter(
              (item) => item !== id,
            )
          : [
              ...current.skill_ids,
              id,
            ],
      };
    });
  }

  async function syncJobSkills(
    jobId,
    selectedSkillIds,
    previousSkillIds = [],
  ) {
    const selected = [
      ...new Set(
        selectedSkillIds.map(String),
      ),
    ];

    const previous = [
      ...new Set(
        previousSkillIds.map(String),
      ),
    ];

    const skillsToAdd =
      selected.filter(
        (skillId) =>
          !previous.includes(skillId),
      );

    const skillsToDelete =
      previous.filter(
        (skillId) =>
          !selected.includes(skillId),
      );

    await Promise.all(
      skillsToAdd.map(
        (skillId) =>
          addJobSkill(jobId, {
            skill_id: skillId,
            is_required: true,
          }),
      ),
    );

    await Promise.all(
      skillsToDelete.map(
        (skillId) =>
          deleteJobSkill(
            jobId,
            skillId,
          ),
      ),
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!form.company_id) {
      setError(
        "Please select a company.",
      );
      return;
    }

    if (!form.title.trim()) {
      setError(
        "Please enter a job title.",
      );
      return;
    }

    if (!form.description.trim()) {
      setError(
        "Please enter a job description.",
      );
      return;
    }

    if (form.skill_ids.length === 0) {
      setError(
        "Please select at least one required skill.",
      );
      return;
    }

    setSaving(true);
    setError("");

    const payload = {
      company_id: form.company_id,
      title: form.title.trim(),
      description:
        form.description.trim(),
      location:
        form.location.trim() || null,
      employment_type:
        form.employment_type || null,
      experience_level:
        form.experience_level || null,
      salary_min:
        form.salary_min === ""
          ? null
          : Number(form.salary_min),
      salary_max:
        form.salary_max === ""
          ? null
          : Number(form.salary_max),
      currency:
        form.currency.trim() ||
        "USD",
      application_deadline:
        form.application_deadline ||
        null,
    };

    try {
      let savedJob;
      let previousSkillIds = [];

      if (editingJobId) {
        const existingJobSkills =
          await getJobSkills(
            editingJobId,
          );

        previousSkillIds =
          Array.isArray(
            existingJobSkills,
          )
            ? existingJobSkills.map(
                (item) =>
                  String(
                    item.skill_id,
                  ),
              )
            : [];

        savedJob =
          await updateJob(
            editingJobId,
            {
              ...payload,
              status: form.status,
            },
          );

        await syncJobSkills(
          savedJob.id,
          form.skill_ids,
          previousSkillIds,
        );

        setJobs((current) =>
          current.map((job) =>
            job.id === savedJob.id
              ? savedJob
              : job,
          ),
        );
      } else {
        savedJob =
          await createJob(
            payload,
          );

        await syncJobSkills(
          savedJob.id,
          form.skill_ids,
        );

        setJobs((current) => [
          savedJob,
          ...current,
        ]);
      }

      setForm(emptyForm);
      setEditingJobId(null);
      setShowForm(false);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
          "";

      if (
        String(detail)
          .toLowerCase()
          .includes("already added")
      ) {
        setError(
          "One or more selected skills are already attached to this job.",
        );
      } else {
        setError(
          detail ||
            "Unable to save the job.",
        );
      }
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(
    job,
    status,
  ) {
    setError("");

    try {
      const updated =
        await updateJob(
          job.id,
          { status },
        );

      setJobs((current) =>
        current.map((item) =>
          item.id === updated.id
            ? updated
            : item,
        ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update job status.",
      );
    }
  }

  function closeForm() {
    setShowForm(false);
    setEditingJobId(null);
    setForm(emptyForm);
    setError("");
  }

  const selectedSkills =
    skills.filter((skill) =>
      form.skill_ids.includes(
        String(skill.id),
      ),
    );

  return (
    <section className="jobs-page">
      <div className="jobs-hero">
        <p className="eyebrow">
          Recruiter
        </p>

        <h1>
          Manage your job postings.
        </h1>

        <p>
          Create roles, update your
          postings, define required skills,
          and control their application
          status.
        </p>
      </div>

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      <Card className="jobs-section-card">
        <div className="jobs-section-header">
          <div>
            <p className="eyebrow">
              Job postings
            </p>

            <h2>
              My jobs
            </h2>
          </div>

          <div className="recruiter-job-header-actions">
            <span className="jobs-count">
              {jobs.length}
            </span>

            <Button
              onClick={startCreate}
            >
              + Create job
            </Button>
          </div>
        </div>

        {loading && (
          <p className="jobs-muted">
            Loading your job postings...
          </p>
        )}

        {!loading &&
          jobs.length === 0 && (
            <div className="recruiter-jobs-empty">
              <h3>
                No job postings yet
              </h3>

              <p>
                Create your first job
                posting to start receiving
                applications.
              </p>

              <Button
                onClick={startCreate}
              >
                Create your first job
              </Button>
            </div>
          )}

        {!loading &&
          jobs.length > 0 && (
            <div className="recruiter-job-list">
              {jobs.map((job) => (
                <article
                  key={job.id}
                  className="recruiter-job-row"
                >
                  <div className="recruiter-job-main">
                    <div>
                      <h3>
                        {job.title}
                      </h3>

                      <p>
                        {job.company_name ||
                          "Company"}
                      </p>

                      <div className="recruiter-job-meta">
                        {job.location && (
                          <span>
                            {job.location}
                          </span>
                        )}

                        {job.employment_type && (
                          <span>
                            {job.employment_type}
                          </span>
                        )}

                        {job.experience_level && (
                          <span>
                            {job.experience_level}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="recruiter-job-actions">
                    <span
                      className={`recruiter-job-status status-${String(
                        job.status,
                      ).toLowerCase()}`}
                    >
                      {job.status}
                    </span>

                    <select
                      value={job.status}
                      onChange={(event) =>
                        handleStatusChange(
                          job,
                          event.target.value,
                        )
                      }
                      aria-label={`Change status for ${job.title}`}
                    >
                      <option value="DRAFT">
                        Draft
                      </option>

                      <option value="OPEN">
                        Open
                      </option>

                      <option value="CLOSED">
                        Closed
                      </option>
                    </select>

                    <Button
                      variant="secondary"
                      onClick={() =>
                        startEdit(job)
                      }
                    >
                      Edit
                    </Button>
                  </div>
                </article>
              ))}
            </div>
          )}
      </Card>

      {showForm && (
        <Card className="jobs-section-card recruiter-job-form-card">
          <div className="jobs-section-header">
            <div>
              <p className="eyebrow">
                {editingJobId
                  ? "Edit posting"
                  : "New posting"}
              </p>

              <h2>
                {editingJobId
                  ? "Edit job"
                  : "Create job"}
              </h2>
            </div>

            <Button
              variant="ghost"
              onClick={closeForm}
            >
              Cancel
            </Button>
          </div>

          <form
            className="recruiter-job-form"
            onSubmit={handleSubmit}
          >
            <label>
              Company

              <select
                name="company_id"
                value={form.company_id}
                onChange={handleChange}
                required
              >
                <option value="">
                  Select company
                </option>

                {companies.map(
                  (company) => (
                    <option
                      key={company.id}
                      value={company.id}
                    >
                      {company.name}
                    </option>
                  ),
                )}
              </select>
            </label>

            <label>
              Job title

              <input
                name="title"
                value={form.title}
                onChange={handleChange}
                placeholder="Backend Software Engineer"
                required
              />
            </label>

            <label>
              Description

              <textarea
                name="description"
                rows="7"
                value={form.description}
                onChange={handleChange}
                placeholder="Describe the role, responsibilities, and requirements..."
                required
              />
            </label>

            <div className="recruiter-job-form-grid">
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
                Employment type

                <select
                  name="employment_type"
                  value={form.employment_type}
                  onChange={handleChange}
                >
                  <option value="">
                    Select type
                  </option>

                  <option value="FULL_TIME">
                    Full time
                  </option>

                  <option value="PART_TIME">
                    Part time
                  </option>

                  <option value="CONTRACT">
                    Contract
                  </option>

                  <option value="INTERNSHIP">
                    Internship
                  </option>
                </select>
              </label>

              <label>
                Experience level

                <select
                  name="experience_level"
                  value={form.experience_level}
                  onChange={handleChange}
                >
                  <option value="">
                    Select level
                  </option>

                  <option value="ENTRY_LEVEL">
                    Entry level
                  </option>

                  <option value="MID_LEVEL">
                    Mid level
                  </option>

                  <option value="SENIOR">
                    Senior
                  </option>

                  <option value="LEAD">
                    Lead
                  </option>
                </select>
              </label>

              <label>
                Currency

                <input
                  name="currency"
                  value={form.currency}
                  onChange={handleChange}
                  placeholder="USD"
                />
              </label>

              <label>
                Minimum salary

                <input
                  name="salary_min"
                  type="number"
                  min="0"
                  value={form.salary_min}
                  onChange={handleChange}
                />
              </label>

              <label>
                Maximum salary

                <input
                  name="salary_max"
                  type="number"
                  min="0"
                  value={form.salary_max}
                  onChange={handleChange}
                />
              </label>

              <label>
                Application deadline

                <input
                  name="application_deadline"
                  type="date"
                  value={
                    form.application_deadline
                  }
                  onChange={handleChange}
                />
              </label>

              {editingJobId && (
                <label>
                  Status

                  <select
                    name="status"
                    value={form.status}
                    onChange={handleChange}
                  >
                    <option value="DRAFT">
                      Draft
                    </option>

                    <option value="OPEN">
                      Open
                    </option>

                    <option value="CLOSED">
                      Closed
                    </option>
                  </select>
                </label>
              )}
            </div>

            <div className="recruiter-job-skills-section">
              <div className="recruiter-job-skills-header">
                <div>
                  <p className="eyebrow">
                    Role requirements
                  </p>

                  <h3>
                    Required skills
                  </h3>

                  <p>
                    Select the skills required
                    for this position. These will
                    be used by MEDAI Skill Gap
                    Analysis when candidates apply.
                  </p>
                </div>

                <span>
                  {form.skill_ids.length} selected
                </span>
              </div>

              {loadingJobSkills && (
                <p className="jobs-muted">
                  Loading current job skills...
                </p>
              )}

              {!loadingJobSkills &&
                skills.length === 0 && (
                  <p className="jobs-muted">
                    No skills are available yet.
                  </p>
                )}

              {!loadingJobSkills &&
                skills.length > 0 && (
                  <div className="recruiter-skills-grid">
                    {skills.map(
                      (skill) => {
                        const selected =
                          form.skill_ids.includes(
                            String(
                              skill.id,
                            ),
                          );

                        return (
                          <button
                            key={skill.id}
                            type="button"
                            className={`recruiter-skill-option${
                              selected
                                ? " selected"
                                : ""
                            }`}
                            onClick={() =>
                              toggleSkill(
                                skill.id,
                              )
                            }
                          >
                            <span>
                              {skill.name}
                            </span>

                            <span>
                              {selected
                                ? "✓"
                                : "+"}
                            </span>
                          </button>
                        );
                      },
                    )}
                  </div>
                )}

              {selectedSkills.length >
                0 && (
                <div className="recruiter-selected-skills">
                  <span>
                    Selected:
                  </span>

                  {selectedSkills.map(
                    (skill) => (
                      <span
                        key={skill.id}
                        className="recruiter-selected-skill"
                      >
                        {skill.name}
                      </span>
                    ),
                  )}
                </div>
              )}
            </div>

            <div className="recruiter-job-form-actions">
              <Button
                type="button"
                variant="ghost"
                onClick={closeForm}
              >
                Cancel
              </Button>

              <Button
                type="submit"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingJobId
                    ? "Save changes"
                    : "Create job"}
              </Button>
            </div>
          </form>
        </Card>
      )}
    </section>
  );
}
