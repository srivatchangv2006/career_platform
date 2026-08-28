import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../../components/ui/Card";

import { getJobs } from "../../../api/jobs.api";

import JobCard from "../shared/JobCard";
import RecommendedJobs from "./RecommendedJobs";

export default function CandidateJobs() {
  const [jobs, setJobs] =
    useState([]);

  const [query, setQuery] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const loadJobs =
    useCallback(async () => {
      setLoading(true);

      try {
        const result =
          await getJobs();

        setJobs(
          Array.isArray(result)
            ? result
            : [],
        );
      } catch {
        setJobs([]);
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Load available jobs.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadJobs();
  }, [loadJobs]);

  const filteredJobs =
    jobs.filter((job) => {
      const value =
        query.trim().toLowerCase();

      if (!value) {
        return true;
      }

      return (
        job.title
          ?.toLowerCase()
          .includes(value) ||
        job.description
          ?.toLowerCase()
          .includes(value) ||
        job.location
          ?.toLowerCase()
          .includes(value) ||
        job.experience_level
          ?.toLowerCase()
          .includes(value) ||
        job.employment_type
          ?.toLowerCase()
          .includes(value)
      );
    });

  return (
    <section className="jobs-page">
      <div className="jobs-hero">
        <p className="eyebrow">
          Candidate
        </p>

        <h1>
          Find your next opportunity.
        </h1>

        <p>
          Explore open roles and discover
          opportunities matched to your
          skills and preferences.
        </p>
      </div>

      <RecommendedJobs />

      <Card className="jobs-section-card">
        <div className="jobs-section-header">
          <div>
            <p className="eyebrow">
              Explore
            </p>

            <h2>
              All jobs
            </h2>
          </div>

          <span className="jobs-count">
            {filteredJobs.length}
          </span>
        </div>

        <input
          className="jobs-search"
          type="search"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder="Search jobs..."
          aria-label="Search jobs"
        />

        {loading && (
          <p className="jobs-muted">
            Loading jobs...
          </p>
        )}

        {!loading &&
          filteredJobs.length === 0 && (
            <p className="jobs-muted">
              No jobs match your search.
            </p>
          )}

        {!loading &&
          filteredJobs.length > 0 && (
            <div className="jobs-list">
              {filteredJobs.map(
                (job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                  />
                ),
              )}
            </div>
          )}
      </Card>
    </section>
  );
}
