import { useEffect, useState } from "react";

import Card from "../../../components/ui/Card";
import Avatar from "../../../components/ui/Avatar";

import { useAuth } from "../../../hooks/useAuth";
import { useProfile } from "../../../hooks/useProfile";

import {
  getMyApplications,
} from "../../../api/dashboard.api";

import CareerSnapshot from "./CareerSnapshot";
import RecommendedJobs from "../../jobs/candidate/RecommendedJobs";
import RecentApplications from "./RecentApplications";

export default function CandidateDashboard() {
  const { user } = useAuth();
  const { profile } = useProfile();

  const [applications, setApplications] =
    useState([]);

  const [
    loadingApplications,
    setLoadingApplications,
  ] = useState(true);

  const displayName =
    profile?.full_name ||
    user?.email?.split("@")[0] ||
    "MEDAI User";

  useEffect(() => {
    let active = true;

    async function loadApplications() {
      try {
        const result =
          await getMyApplications();

        if (active) {
          setApplications(
            Array.isArray(result)
              ? result
              : [],
          );
        }
      } catch {
        if (active) {
          setApplications([]);
        }
      } finally {
        if (active) {
          setLoadingApplications(false);
        }
      }
    }

    loadApplications();

    return () => {
      active = false;
    };
  }, []);

  const interviewCount =
    applications.filter(
      (application) =>
        application.status ===
        "INTERVIEW",
    ).length;

  return (
    <section className="dashboard-page">
      <div className="dashboard-hero">
        <div className="dashboard-hero-content">
          <p className="eyebrow">
            Candidate Dashboard
          </p>

          <h1>
            Good to see you, {displayName}.
          </h1>

          <p>
            Keep building your profile,
            exploring opportunities, and
            moving your career forward.
          </p>
        </div>

        <Avatar
          name={displayName}
          src={
            profile?.profile_image_blob_path ||
            null
          }
          size="large"
        />
      </div>

      <CareerSnapshot
        applicationCount={
          applications.length
        }
        interviewCount={
          interviewCount
        }
        connectionCount={0}
      />

      <div className="dashboard-main-grid">
        <div className="dashboard-primary-column">
          <RecommendedJobs />

          <RecentApplications
            applications={applications}
            loading={
              loadingApplications
            }
          />
        </div>

        <aside className="dashboard-secondary-column">
          <Card className="dashboard-section-card">
            <p className="eyebrow">
              MEDAI
            </p>

            <h2>
              Complete your profile
            </h2>

            <p className="dashboard-muted">
              A complete professional
              profile makes it easier for
              recruiters and other
              professionals to discover you.
            </p>
          </Card>

          <Card className="dashboard-section-card">
            <p className="eyebrow">
              Community
            </p>

            <h2>
              Share your journey
            </h2>

            <p className="dashboard-muted">
              Share projects, experiences,
              achievements, and ideas with
              the MEDAI community.
            </p>
          </Card>
        </aside>
      </div>
    </section>
  );
}
