import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../../components/ui/Card";

import {
  generateJobRecommendations,
  getRecommendationItems,
} from "../../../api/dashboard.api";

import {
  getJob,
} from "../../../api/jobs.api";

import JobCard from "../shared/JobCard";

export default function RecommendedJobs() {
  const [
    recommendations,
    setRecommendations,
  ] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const loadRecommendations =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const run =
          await generateJobRecommendations();

        const items =
          await getRecommendationItems(
            run.id,
          );

        const enriched =
          await Promise.all(
            items.map(
              async (item) => {
                try {
                  const job =
                    await getJob(
                      item.job_id,
                    );

                  return {
                    item,
                    job,
                  };
                } catch {
                  return null;
                }
              },
            ),
          );

        setRecommendations(
          enriched.filter(Boolean),
        );
      } catch (err) {
        setRecommendations([]);

        setError(
          err?.response?.data?.detail ||
            "Unable to generate job recommendations.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Generate AI recommendations when the section loads.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadRecommendations();
  }, [loadRecommendations]);

  return (
    <Card className="jobs-section-card">
      <div className="jobs-section-header">
        <div>
          <p className="eyebrow">
            AI-powered
          </p>

          <h2>
            Recommended for you
          </h2>
        </div>
      </div>

      {loading && (
        <p className="jobs-muted">
          Finding opportunities that match
          your profile...
        </p>
      )}

      {error && (
        <div className="jobs-info-message">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        recommendations.length === 0 && (
          <p className="jobs-muted">
            No matching jobs were found yet.
          </p>
        )}

      <div className="jobs-list">
        {recommendations.map(
          ({ item, job }) => (
            <JobCard
              key={item.id}
              job={job}
              recommendation={item}
            />
          ),
        )}
      </div>
    </Card>
  );
}
