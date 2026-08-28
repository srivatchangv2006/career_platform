import {
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getReferralJobs,
  getReferralOpportunities,
  createReferralOpportunity,
  createReferralRequest,
  deleteReferralOpportunity,
  getReceivedReferralRequests,
  getSentReferralRequests,
  getReferralResumeBlob,
  updateReferralOpportunity,
  updateReferralRequest,
} from "../../api/referrals.api";

import {
  getMyResumes,
} from "../../api/resumes.api";


import { useAuth } from "../../hooks/useAuth";


function CreateOpportunityModal({
  jobs,
  onCreated,
  onClose,
}) {
  const [referralType, setReferralType] =
    useState("JOB");

  const [jobId, setJobId] =
    useState("");

  const [opportunityTitle, setOpportunityTitle] =
    useState("");

  const [opportunityCompany, setOpportunityCompany] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [maxReferrals, setMaxReferrals] =
    useState("");

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    if (
      referralType === "JOB" &&
      !jobId
    ) {
      setError(
        "Please select a job.",
      );
      return;
    }

    if (
      referralType === "OTHER" &&
      (
        !opportunityCompany.trim() ||
        !opportunityTitle.trim()
      )
    ) {
      setError(
        "Please enter the company and opportunity title.",
      );
      return;
    }

    setSaving(true);
    setError("");

    try {
      const result =
        await createReferralOpportunity({
          job_id:
            referralType === "JOB"
              ? jobId
              : null,

          opportunity_title:
            referralType === "OTHER"
              ? opportunityTitle.trim()
              : null,

          opportunity_company:
            referralType === "OTHER"
              ? opportunityCompany.trim()
              : null,

          message:
            message.trim() || null,

          max_referrals:
            maxReferrals === ""
              ? null
              : Number(
                  maxReferrals,
                ),
        });

      onCreated(result);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create referral opportunity.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="referral-modal-backdrop">
      <div
        className="referral-modal"
        role="dialog"
        aria-modal="true"
      >
        <button
          type="button"
          className="referral-modal-close"
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>

        <p className="eyebrow">
          Referrals
        </p>

        <h2>
          Offer a referral
        </h2>

        <p className="referral-modal-subtitle">
          Share an opportunity where you can
          help another candidate get a referral.
        </p>

        {error && (
          <div className="referral-message">
            {error}
          </div>
        )}

        <form
          className="referral-form"
          onSubmit={handleSubmit}
        >
          <label>
            Referral type

            <select
              value={referralType}
              onChange={(event) => {
                setReferralType(
                  event.target.value,
                );

                setError("");
              }}
            >
              <option value="JOB">
                Platform job
              </option>

              <option value="OTHER">
                Other opportunity
              </option>
            </select>
          </label>

          {referralType === "JOB" ? (
            <label>
              Job

              <select
                value={jobId}
                onChange={(event) =>
                  setJobId(
                    event.target.value,
                  )
                }
                required
                disabled={
                  jobs.length === 0
                }
              >
                <option value="">
                  {jobs.length === 0
                    ? "No open jobs available"
                    : "Select a job"}
                </option>

                {jobs.map((job) => (
                  <option
                    key={job.id}
                    value={job.id}
                  >
                    {job.title}
                    {job.company_name
                      ? ` — ${job.company_name}`
                      : ""}
                  </option>
                ))}
              </select>

              {jobs.length === 0 && (
                <span className="referral-field-hint">
                  No OPEN jobs were returned
                  by the jobs service.
                </span>
              )}
            </label>
          ) : (
            <>
              <label>
                Company

                <input
                  type="text"
                  value={
                    opportunityCompany
                  }
                  onChange={(event) =>
                    setOpportunityCompany(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Microsoft"
                  maxLength={200}
                  required
                />
              </label>

              <label>
                Opportunity

                <input
                  type="text"
                  value={
                    opportunityTitle
                  }
                  onChange={(event) =>
                    setOpportunityTitle(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Software Engineer"
                  maxLength={200}
                  required
                />
              </label>
            </>
          )}

          <label>
            Referral message

            <textarea
              rows="5"
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
              placeholder="Tell candidates why you can refer them..."
            />
          </label>

          <label>
            Maximum referrals

            <input
              type="number"
              min="1"
              value={maxReferrals}
              onChange={(event) =>
                setMaxReferrals(
                  event.target.value,
                )
              }
              placeholder="Leave blank for unlimited"
            />
          </label>

          <div className="referral-form-actions">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Creating..."
                : "Create opportunity"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

function RequestReferralModal({
  opportunity,
  resumes,
  onCreated,
  onClose,
}) {
  const [resumeId, setResumeId] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [sending, setSending] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setSending(true);
    setError("");

    try {
      const result =
        await createReferralRequest(
          opportunity.id,
          {
            resume_id:
              resumeId || null,
            message:
              message.trim() || null,
          },
        );

      onCreated(result);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to request referral.",
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="referral-modal-backdrop">
      <div
        className="referral-modal"
        role="dialog"
        aria-modal="true"
      >
        <button
          type="button"
          className="referral-modal-close"
          onClick={onClose}
        >
          ×
        </button>

        <p className="eyebrow">
          Request referral
        </p>

        <h2>
          {opportunity.job_title}
        </h2>

        <p className="referral-company">
          {opportunity.company_name}
        </p>

        {error && (
          <div className="referral-message">
            {error}
          </div>
        )}

        <form
          className="referral-form"
          onSubmit={handleSubmit}
        >
          <label>
            Resume

            <select
              value={resumeId}
              onChange={(event) =>
                setResumeId(
                  event.target.value,
                )
              }
            >
              <option value="">
                No resume selected
              </option>

              {resumes.map((resume) => (
                <option
                  key={resume.id}
                  value={resume.id}
                >
                  {resume.file_name}
                  {resume.is_primary
                    ? " — Default"
                    : ""}
                </option>
              ))}
            </select>
          </label>

          <label>
            Message

            <textarea
              rows="6"
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
              placeholder="Introduce yourself and explain why you're requesting the referral..."
            />
          </label>

          <div className="referral-form-actions">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={sending}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              disabled={sending}
            >
              {sending
                ? "Sending..."
                : "Request referral"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}


export default function ReferralsPage() {
  const { user } =
    useAuth();

  const [opportunities, setOpportunities] =
    useState([]);

  const [sentRequests, setSentRequests] =
    useState([]);

  const [receivedRequests, setReceivedRequests] =
    useState([]);

  const [jobs, setJobs] =
    useState([]);

  const [resumes, setResumes] =
    useState([]);

  const [showCreate, setShowCreate] =
    useState(false);

  const [selectedOpportunity, setSelectedOpportunity] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function loadReferralData() {
      if (active) {
        setLoading(true);
        setError("");
      }

      try {
        const [
          opportunitiesResult,
          sentResult,
          receivedResult,
          jobsResult,
          resumesResult,
        ] = await Promise.all([
          getReferralOpportunities(),
          getSentReferralRequests(),
          getReceivedReferralRequests(),
          getReferralJobs(),
          getMyResumes(),
        ]);

        const uniqueJobs = Array.isArray(
          jobsResult,
        )
          ? jobsResult
          : [];

        if (!active) {
          return;
        }

        setOpportunities(
          Array.isArray(
            opportunitiesResult,
          )
            ? opportunitiesResult
            : [],
        );

        setSentRequests(
          Array.isArray(sentResult)
            ? sentResult
            : [],
        );

        setReceivedRequests(
          Array.isArray(receivedResult)
            ? receivedResult
            : [],
        );

        setJobs(uniqueJobs);

        setResumes(
          Array.isArray(resumesResult)
            ? resumesResult
            : [],
        );
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load referrals.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadReferralData();

    return () => {
      active = false;
    };
  }, []);

  function handleOpportunityCreated(
    opportunity,
  ) {
    setOpportunities((current) => [
      opportunity,
      ...current,
    ]);

    setShowCreate(false);
  }

  function handleReferralCreated(
    referral,
  ) {
    setSentRequests((current) => [
      referral,
      ...current,
    ]);

    setSelectedOpportunity(
      null,
    );
  }

  async function handleReferralResume(
    referralId,
  ) {
    try {
      const blob =
        await getReferralResumeBlob(
          referralId,
        );

      const url =
        URL.createObjectURL(blob);

      window.open(
        url,
        "_blank",
        "noopener,noreferrer",
      );

      setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 60000);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to open the resume.",
      );
    }
  }

  async function handleRequestStatus(
    referralId,
    status,
  ) {
    try {
      const updated =
        await updateReferralRequest(
          referralId,
          {
            status,
          },
        );

      setReceivedRequests(
        (current) =>
          current.map(
            (referral) =>
              referral.id ===
              referralId
                ? updated
                : referral,
          ),
      );

      const [
        refreshedOpportunities,
        refreshedSent,
        refreshedReceived,
      ] = await Promise.all([
        getReferralOpportunities(),
        getSentReferralRequests(),
        getReceivedReferralRequests(),
      ]);

      setOpportunities(
        Array.isArray(
          refreshedOpportunities,
        )
          ? refreshedOpportunities
          : [],
      );

      setSentRequests(
        Array.isArray(
          refreshedSent,
        )
          ? refreshedSent
          : [],
      );

      setReceivedRequests(
        Array.isArray(
          refreshedReceived,
        )
          ? refreshedReceived
          : [],
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update referral request.",
      );
    }
  }

  async function handleOpportunityStatus(
    opportunity,
    status,
  ) {
    try {
      const updated =
        await updateReferralOpportunity(
          opportunity.id,
          {
            status,
          },
        );

      setOpportunities(
        (current) =>
          current.map(
            (item) =>
              item.id ===
              opportunity.id
                ? updated
                : item,
          ),
      );

      const [
        refreshedOpportunities,
        refreshedSent,
        refreshedReceived,
      ] = await Promise.all([
        getReferralOpportunities(),
        getSentReferralRequests(),
        getReceivedReferralRequests(),
      ]);

      setOpportunities(
        Array.isArray(
          refreshedOpportunities,
        )
          ? refreshedOpportunities
          : [],
      );

      setSentRequests(
        Array.isArray(
          refreshedSent,
        )
          ? refreshedSent
          : [],
      );

      setReceivedRequests(
        Array.isArray(
          refreshedReceived,
        )
          ? refreshedReceived
          : [],
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update referral opportunity.",
      );
    }
  }

  async function handleDeleteOpportunity(
    opportunityId,
  ) {
    try {
      await deleteReferralOpportunity(
        opportunityId,
      );

      setOpportunities(
        (current) =>
          current.filter(
            (item) =>
              item.id !==
              opportunityId,
          ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to delete referral opportunity.",
      );
    }
  }

  const ownOpportunities =
    opportunities.filter(
      (opportunity) =>
        String(
          opportunity.posted_by,
        ) ===
        String(user?.id),
    );

  const availableOpportunities =
    opportunities.filter(
      (opportunity) =>
        String(
          opportunity.posted_by,
        ) !==
        String(user?.id),
    );

  if (loading) {
    return (
      <Card className="feed-state">
        Loading referrals...
      </Card>
    );
  }

  return (
    <section className="referrals-page">
      <div className="referrals-hero">
        <div>
          <p className="eyebrow">
            MEDAI
          </p>

          <h1>
            Referrals
          </h1>

          <p>
            Help people get connected to
            opportunities, and find someone who
            can refer you.
          </p>
        </div>

        <Button
          onClick={() =>
            setShowCreate(true)
          }
        >
          + Offer a referral
        </Button>
      </div>

      {error && (
        <div className="referral-message">
          {error}
        </div>
      )}

      <Card className="referral-section-card">
        <div className="referral-section-header">
          <div>
            <p className="eyebrow">
              Opportunities
            </p>

            <h2>
              Available referrals
            </h2>
          </div>

          <span className="referral-count">
            {availableOpportunities.length}
          </span>
        </div>

        {availableOpportunities.length ===
        0 ? (
          <div className="referral-empty">
            <h3>
              No referral opportunities
            </h3>

            <p>
              New opportunities will appear
              here when someone offers a referral.
            </p>
          </div>
        ) : (
          <div className="referral-list">
            {availableOpportunities.map(
              (opportunity) => (
                <div
                  key={opportunity.id}
                  className="referral-opportunity-card"
                >
                  <div>
                    <h3>
                      {opportunity.job_title}
                    </h3>

                    <p className="referral-company">
                      {opportunity.company_name}
                    </p>

                    {opportunity.is_external && (
                      <span className="referral-external-badge">
                        Other opportunity
                      </span>
                    )}

                    <p className="referral-poster">
                      Offered by{" "}
                      <strong>
                        {
                          opportunity.posted_by_name
                        }
                      </strong>
                    </p>

                    {opportunity.message && (
                      <p className="referral-message-text">
                        {opportunity.message}
                      </p>
                    )}
                  </div>

                  <div className="referral-opportunity-side">
                    <span className="referral-capacity">
                      {opportunity.remaining_referrals ===
                      null
                        ? "Unlimited"
                        : `${opportunity.remaining_referrals} remaining`}
                    </span>

                    {opportunity.remaining_referrals !==
                      0 && (
                      <Button
                        onClick={() =>
                          setSelectedOpportunity(
                            opportunity,
                          )
                        }
                      >
                        Request referral
                      </Button>
                    )}
                  </div>
                </div>
              ),
            )}
          </div>
        )}
      </Card>

      <div className="referral-columns">
        <Card className="referral-section-card">
          <div className="referral-section-header">
            <div>
              <p className="eyebrow">
                Requests
              </p>

              <h2>
                My requests
              </h2>
            </div>
          </div>

          {sentRequests.length === 0 ? (
            <div className="referral-empty">
              <p>
                You haven't requested a
                referral yet.
              </p>
            </div>
          ) : (
            <div className="referral-list">
              {sentRequests.map(
                (referral) => (
                  <div
                    key={referral.id}
                    className="referral-request-card"
                  >
                    <div>
                      <strong>
                        {referral.resume_name ||
                          "No resume attached"}
                      </strong>

                      {referral.message && (
                        <p>
                          {referral.message}
                        </p>
                      )}

                      <span>
                        Request ID:{" "}
                        {referral.id.slice(
                          0,
                          8,
                        )}
                      </span>
                    </div>

                    <span
                      className={`referral-status referral-status-${referral.status.toLowerCase()}`}
                    >
                      {referral.status}
                    </span>
                  </div>
                ),
              )}
            </div>
          )}
        </Card>

        <Card className="referral-section-card">
          <div className="referral-section-header">
            <div>
              <p className="eyebrow">
                Incoming
              </p>

              <h2>
                Referral requests
              </h2>
            </div>
          </div>

          {receivedRequests.length ===
          0 ? (
            <div className="referral-empty">
              <p>
                No referral requests yet.
              </p>
            </div>
          ) : (
            <div className="referral-list">
              {receivedRequests.map(
                (referral) => (
                  <div
                    key={referral.id}
                    className="referral-request-card"
                  >
                    <div>
                      <strong>
                        {
                          referral.requester_name
                        }
                      </strong>

                      <div className="referral-resume-row">
                        <div>
                          <span className="referral-resume-label">
                            Resume
                          </span>

                          <strong>
                            {referral.resume_name ||
                              "No resume attached"}
                          </strong>
                        </div>

                        {referral.resume_id && (
                          <button
                            type="button"
                            className="referral-resume-link"
                            onClick={() =>
                              handleReferralResume(
                                referral.id,
                              )
                            }
                          >
                            View resume
                          </button>
                        )}
                      </div>

                      {referral.message && (
                        <p>
                          {referral.message}
                        </p>
                      )}
                    </div>

                    <div className="referral-request-actions">
                      <span
                        className={`referral-status referral-status-${referral.status.toLowerCase()}`}
                      >
                        {referral.status}
                      </span>

                      {referral.status ===
                        "PENDING" && (
                        <>
                          <Button
                            onClick={() =>
                              handleRequestStatus(
                                referral.id,
                                "ACCEPTED",
                              )
                            }
                          >
                            Accept
                          </Button>

                          <Button
                            variant="ghost"
                            onClick={() =>
                              handleRequestStatus(
                                referral.id,
                                "REJECTED",
                              )
                            }
                          >
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ),
              )}
            </div>
          )}
        </Card>
      </div>

      <Card className="referral-section-card">
        <div className="referral-section-header">
          <div>
            <p className="eyebrow">
              My opportunities
            </p>

            <h2>
              Referral opportunities I'm offering
            </h2>
          </div>
        </div>

        {ownOpportunities.length ===
        0 ? (
          <div className="referral-empty">
            <p>
              You are not offering any
              referrals yet.
            </p>
          </div>
        ) : (
          <div className="referral-list">
            {ownOpportunities.map(
              (opportunity) => (
                <div
                  key={opportunity.id}
                  className="referral-request-card"
                >
                  <div>
                    <strong>
                      {
                        opportunity.job_title
                      }
                    </strong>

                    <p>
                      {opportunity.company_name}
                    </p>

                    <span>
                      {opportunity.accepted_referrals} accepted
                      {opportunity.max_referrals !==
                      null
                        ? ` / ${opportunity.max_referrals}`
                        : ""}
                    </span>
                  </div>

                  <div className="referral-request-actions">
                    <span
                      className={`referral-status referral-status-${opportunity.status.toLowerCase()}`}
                    >
                      {opportunity.status}
                    </span>

                    <Button
                      variant="ghost"
                      onClick={() =>
                        handleOpportunityStatus(
                          opportunity,
                          opportunity.status ===
                            "OPEN"
                            ? "CLOSED"
                            : "OPEN",
                        )
                      }
                    >
                      {opportunity.status ===
                      "OPEN"
                        ? "Close"
                        : "Reopen"}
                    </Button>

                    <Button
                      variant="ghost"
                      onClick={() =>
                        handleDeleteOpportunity(
                          opportunity.id,
                        )
                      }
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ),
            )}
          </div>
        )}
      </Card>

      {showCreate && (
        <CreateOpportunityModal
          jobs={jobs}
          onCreated={
            handleOpportunityCreated
          }
          onClose={() =>
            setShowCreate(false)
          }
        />
      )}

      {selectedOpportunity && (
        <RequestReferralModal
          opportunity={
            selectedOpportunity
          }
          resumes={resumes}
          onCreated={
            handleReferralCreated
          }
          onClose={() =>
            setSelectedOpportunity(
              null,
            )
          }
        />
      )}
    </section>
  );
}
