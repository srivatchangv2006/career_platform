import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getFollowers,
} from "../../api/networking.api";

import UserMiniCard from "./UserMiniCard";
import NetworkPeopleModal from "./NetworkPeopleModal";

export default function FollowersList({
  userId,
}) {
  const [followers, setFollowers] =
    useState([]);

  const [query, setQuery] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [modalOpen, setModalOpen] =
    useState(false);

  const [modalQuery, setModalQuery] =
    useState("");

  const loadFollowers =
    useCallback(
      async (searchValue = "") => {
        setLoading(true);

        try {
          const result =
            await getFollowers(
              userId,
              searchValue,
            );

          setFollowers(
            Array.isArray(result)
              ? result
              : [],
          );
        } catch {
          setFollowers([]);
        } finally {
          setLoading(false);
        }
      },
      [userId],
    );

  useEffect(() => {
    // Load followers when the viewed user changes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadFollowers();
  }, [loadFollowers]);

  useEffect(() => {
    if (!modalOpen) {
      return undefined;
    }

    const timeoutId =
      setTimeout(() => {
        loadFollowers(
          modalQuery.trim(),
        );
      }, 250);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [
    modalOpen,
    modalQuery,
    loadFollowers,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    loadFollowers(
      query.trim(),
    );
  }

  const people = followers
    .map(
      (follow) =>
        follow.follower,
    )
    .filter(Boolean);

  return (
    <>
      <Card className="network-section-card">
        <div className="network-section-header">
          <div>
            <p className="eyebrow">
              People
            </p>

            <h2>
              Followers
            </h2>
          </div>

          <span className="network-count">
            {people.length}
          </span>
        </div>

        <form
          className="network-search-form"
          onSubmit={handleSearch}
        >
          <input
            type="search"
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            placeholder="Search followers..."
            aria-label="Search followers"
          />

          <Button
            type="submit"
            variant="secondary"
          >
            Search
          </Button>
        </form>

        {loading && (
          <p className="network-muted">
            Loading followers...
          </p>
        )}

        {!loading &&
          people.length > 0 && (
            <div className="network-preview-list">
              {people
                .slice(0, 2)
                .map((person) => (
                  <UserMiniCard
                    key={person.user_id}
                    user={person}
                  />
                ))}
            </div>
          )}

        {!loading &&
          people.length === 0 && (
            <p className="network-muted">
              You don't have any followers yet.
            </p>
          )}

        {people.length > 2 && (
          <Button
            variant="secondary"
            onClick={() =>
              setModalOpen(true)
            }
            className="network-view-all-button"
          >
            View all {people.length}
          </Button>
        )}
      </Card>

      {modalOpen && (
        <NetworkPeopleModal
          title="Followers"
          users={people}
          query={modalQuery}
          setQuery={setModalQuery}
          onClose={() => {
            setModalOpen(false);
            setModalQuery("");
          }}
          loading={loading}
        />
      )}
    </>
  );
}
