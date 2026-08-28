import { useEffect, useState } from "react";

import Avatar from "../../../components/ui/Avatar";
import Card from "../../../components/ui/Card";
import { useAuth } from "../../../hooks/useAuth";
import { useProfile } from "../../../hooks/useProfile";
import { getDisplayName } from "../../../utils/getDisplayHandle";
import {
  getRecruiterDashboard,
  getRecruiterApplicants,
} from "../../../api/dashboard.api";

import HiringSnapshot from "./HiringSnapshot";
import ApplicationPipeline from "./ApplicationPipeline";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const { profile } = useProfile();

  const [dashboard, setDashboard] =
    useState(null);

  const [applicants, setApplicants] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const displayName =
    profile?.full_name ||
    profile?.designation ||
    getDisplayName(user?.email);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        const [
          dashboardResult,
          applicantsResult,
        ] = await Promise.all([
          getRecruiterDashboard(),
          getRecruiterApplicants(),
        ]);

        if (active) {
          setDashboard(
            dashboardResult,
          );

          setApplicants(
            applicantsResult,
          );
        }
      } catch {
        if (active) {
          setDashboard(null);
          setApplicants([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <section className="dashboard-page">
        <Card className="feed-state">
          Loading recruiter dashboard...
        </Card>
      </section>
    );
  }

  if (!dashboard) {
    return (
      <section className="dashboard-page">
        <Card className="feed-state feed-error">
          Unable to load recruiter
          dashboard data.
        </Card>
      </section>
    );
  }

  return (
    <section className="dashboard-page">
      <div className="dashboard-hero">
        <div className="dashboard-hero-content">
          <p className="eyebrow">
            Recruiter Dashboard
          </p>

          <h1>
            Good to see you, {displayName}.
          </h1>

          <p>
            Manage your hiring pipeline,
            review applicants, and keep your
            open roles moving.
          </p>
        </div>

        <Avatar
          name={displayName}
          size="large"
        />
      </div>

      <HiringSnapshot
        totalJobs={
          dashboard.total_jobs
        }
        openJobs={
          dashboard.open_jobs
        }
        totalApplications={
          dashboard.total_applications
        }
        upcomingInterviews={
          dashboard.upcoming_interviews
        }
      />

      <div className="dashboard-main-grid">
        <div className="dashboard-primary-column">
          <ApplicationPipeline
            counts={
              dashboard.applications_by_status
            }
          />

          <Card className="dashboard-section-card">
            <div className="dashboard-section-header">
              <div>
                <p className="eyebrow">
                  Hiring activity
                </p>

                <h2>
                  Recent applicants
                </h2>
              </div>
            </div>

            {applicants.length === 0 ? (
              <p className="dashboard-muted">
                No applicants yet.
              </p>
            ) : (
              <div className="dashboard-application-list">
                {applicants
                  .slice(0, 6)
                  .map((applicant) => (
                    <article
                      key={applicant.id}
                      className="dashboard-application-item"
                    >
                      <div>
                        <h3>
                          {
                            applicant.candidate_name ||
                            applicant.candidate_email
                          }
                        </h3>

                        <p>
                          {
                            applicant.job_title
                          }
                        </p>
                      </div>

                      <span className="dashboard-status">
                        {applicant.status}
                      </span>
                    </article>
                  ))}
              </div>
            )}
          </Card>
        </div>

        <aside className="dashboard-secondary-column">
          <Card className="dashboard-section-card">
            <p className="eyebrow">
              Hiring focus
            </p>

            <h2>
              Keep your pipeline moving
            </h2>

            <p className="dashboard-muted">
              Review recent applicants,
              schedule interviews, and keep
              candidates updated.
            </p>
          </Card>
        </aside>
      </div>
    </section>
  );
}
