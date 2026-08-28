import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getMyFollowing,
  unfollowUser,
} from "../../api/networking.api";

import UserMiniCard from "./UserMiniCard";
import NetworkPeopleModal from "./NetworkPeopleModal";

export default function FollowingList() {
  const [following, setFollowing] =
    useState([]);

  const [query, setQuery] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [modalOpen, setModalOpen] =
    useState(false);

  const [modalQuery, setModalQuery] =
    useState("");

  const [removing, setRemoving] =
    useState(null);

  const loadFollowing =
    useCallback(
      async (searchValue = "") => {
        setLoading(true);

        try {
          const result =
            await getMyFollowing(
              searchValue,
            );

          setFollowing(
            Array.isArray(result)
              ? result
              : [],
          );
        } catch {
          setFollowing([]);
        } finally {
          setLoading(false);
        }
      },
      [],
    );

  useEffect(() => {
    // Initial following load.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadFollowing();
  }, [loadFollowing]);

  useEffect(() => {
    if (!modalOpen) {
      return undefined;
    }

    const timeoutId =
      setTimeout(() => {
        loadFollowing(
          modalQuery.trim(),
        );
      }, 250);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [
    modalOpen,
    modalQuery,
    loadFollowing,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    const value = query.trim();

    setSearch(value);
    loadFollowing(value);
  }

  async function handleUnfollow(
    userId,
  ) {
    setRemoving(userId);

    try {
      await unfollowUser(userId);
      await loadFollowing(search);
    } finally {
      setRemoving(null);
    }
  }

  const people = following
    .map(
      (follow) =>
        follow.following,
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
              Following
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
            placeholder="Search following..."
            aria-label="Search following"
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
            Loading following...
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
                    actionLabel="Unfollow"
                    actionDisabled={
                      removing !== null
                    }
                    onAction={() =>
                      handleUnfollow(
                        person.user_id,
                      )
                    }
                  />
                ))}
            </div>
          )}

        {!loading &&
          people.length === 0 && (
            <p className="network-muted">
              You aren't following anyone yet.
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
          title="Following"
          users={people}
          query={modalQuery}
          setQuery={setModalQuery}
          onClose={() => {
            setModalOpen(false);
            setModalQuery("");
          }}
          loading={loading}
          renderAction={(person) => (
            <Button
              variant="secondary"
              disabled={
                removing !== null
              }
              onClick={() =>
                handleUnfollow(
                  person.user_id,
                )
              }
            >
              Unfollow
            </Button>
          )}
        />
      )}
    </>
  );
}
