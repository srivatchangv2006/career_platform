import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getConnectionRequests,
  updateConnection,
} from "../../api/networking.api";

import UserMiniCard from "./UserMiniCard";
import NetworkPeopleModal from "./NetworkPeopleModal";

export default function ConnectionRequests() {
  const [requests, setRequests] =
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

  const [actionLoading, setActionLoading] =
    useState(null);

  const loadRequests =
    useCallback(
      async (searchValue = "") => {
        setLoading(true);

        try {
          const result =
            await getConnectionRequests(
              searchValue,
            );

          setRequests(
            Array.isArray(result)
              ? result
              : [],
          );
        } catch {
          setRequests([]);
        } finally {
          setLoading(false);
        }
      },
      [],
    );

  useEffect(() => {
    // Initial connection-request load.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadRequests();
  }, [loadRequests]);

  useEffect(() => {
    if (!modalOpen) {
      return undefined;
    }

    const timeoutId =
      setTimeout(() => {
        loadRequests(
          modalQuery.trim(),
        );
      }, 250);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [
    modalOpen,
    modalQuery,
    loadRequests,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    const value = query.trim();

    setSearch(value);
    loadRequests(value);
  }

  async function handleUpdate(
    connectionId,
    status,
  ) {
    setActionLoading(connectionId);

    try {
      await updateConnection(
        connectionId,
        status,
      );

      await loadRequests(search);
    } finally {
      setActionLoading(null);
    }
  }

  const people = requests
    .map(
      (request) =>
        request.requester,
    )
    .filter(Boolean);

  function getRequestForUser(userId) {
    return requests.find(
      (request) =>
        request.requester?.user_id ===
        userId,
    );
  }

  function renderActions(person) {
    const request =
      getRequestForUser(
        person.user_id,
      );

    if (!request) {
      return null;
    }

    return (
      <div className="network-request-actions">
        <Button
          disabled={
            actionLoading ===
            request.id
          }
          onClick={() =>
            handleUpdate(
              request.id,
              "ACCEPTED",
            )
          }
        >
          Accept
        </Button>

        <Button
          variant="secondary"
          disabled={
            actionLoading ===
            request.id
          }
          onClick={() =>
            handleUpdate(
              request.id,
              "REJECTED",
            )
          }
        >
          Reject
        </Button>
      </div>
    );
  }

  return (
    <>
      <Card className="network-section-card">
        <div className="network-section-header">
          <div>
            <p className="eyebrow">
              Invitations
            </p>

            <h2>
              Connection requests
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
            placeholder="Search requests..."
            aria-label="Search connection requests"
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
            Loading requests...
          </p>
        )}

        {!loading &&
          people.length > 0 && (
            <div className="network-preview-list">
              {people
                .slice(0, 2)
                .map((person) => (
                  <div
                    key={person.user_id}
                    className="network-request-preview"
                  >
                    <UserMiniCard
                      user={person}
                    />

                    {renderActions(
                      person,
                    )}
                  </div>
                ))}
            </div>
          )}

        {!loading &&
          people.length === 0 && (
            <p className="network-muted">
              No connection requests found.
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
          title="Connection requests"
          users={people}
          query={modalQuery}
          setQuery={setModalQuery}
          onClose={() => {
            setModalOpen(false);
            setModalQuery("");
          }}
          loading={loading}
          renderAction={
            renderActions
          }
        />
      )}
    </>
  );
}
