import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getMyConnections,
  deleteConnection,
} from "../../api/networking.api";

import UserMiniCard from "./UserMiniCard";
import NetworkPeopleModal from "./NetworkPeopleModal";

export default function MyConnections({
  currentUserId,
}) {
  const [connections, setConnections] =
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

  const loadConnections =
    useCallback(
      async (searchValue = "") => {
        setLoading(true);

        try {
          const result =
            await getMyConnections(
              searchValue,
            );

          setConnections(
            Array.isArray(result)
              ? result
              : [],
          );
        } catch {
          setConnections([]);
        } finally {
          setLoading(false);
        }
      },
      [],
    );

  useEffect(() => {
    // Initial connections load.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadConnections();
  }, [loadConnections]);

  useEffect(() => {
    if (!modalOpen) {
      return undefined;
    }

    const timeoutId =
      setTimeout(() => {
        loadConnections(
          modalQuery.trim(),
        );
      }, 250);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [
    modalOpen,
    modalQuery,
    loadConnections,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    const value = query.trim();

    setSearch(value);
    loadConnections(value);
  }

  function getOtherUser(connection) {
    const requesterId =
      connection.requester?.user_id ||
      connection.requester_id;

    const receiverId =
      connection.receiver?.user_id ||
      connection.receiver_id;

    if (
      String(requesterId) ===
      String(currentUserId)
    ) {
      return (
        connection.receiver ||
        null
      );
    }

    if (
      String(receiverId) ===
      String(currentUserId)
    ) {
      return (
        connection.requester ||
        null
      );
    }

    return (
      connection.requester ||
      connection.receiver ||
      null
    );
  }

  async function handleRemove(
    connectionId,
  ) {
    setRemoving(connectionId);

    try {
      await deleteConnection(
        connectionId,
      );

      await loadConnections(search);
    } finally {
      setRemoving(null);
    }
  }

  const people = connections
    .map(getOtherUser)
    .filter(Boolean);

  function getConnectionForPerson(
    person,
  ) {
    return connections.find(
      (connection) =>
        getOtherUser(connection)
          ?.user_id ===
        person.user_id,
    );
  }

  function renderRemoveAction(
    person,
  ) {
    const connection =
      getConnectionForPerson(
        person,
      );

    if (!connection) {
      return null;
    }

    return (
      <Button
        variant="secondary"
        disabled={
          removing === connection.id
        }
        onClick={() =>
          handleRemove(
            connection.id,
          )
        }
      >
        Remove
      </Button>
    );
  }

  return (
    <>
      <Card className="network-section-card">
        <div className="network-section-header">
          <div>
            <p className="eyebrow">
              Your network
            </p>

            <h2>
              My connections
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
            placeholder="Search connections..."
            aria-label="Search connections"
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
            Loading connections...
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
                    actionLabel="Remove"
                    actionDisabled={
                      removing !== null
                    }
                    onAction={() => {
                      const connection =
                        getConnectionForPerson(
                          person,
                        );

                      if (connection) {
                        handleRemove(
                          connection.id,
                        );
                      }
                    }}
                  />
                ))}
            </div>
          )}

        {!loading &&
          people.length === 0 && (
            <p className="network-muted">
              No connections found.
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
          title="My connections"
          users={people}
          query={modalQuery}
          setQuery={setModalQuery}
          onClose={() => {
            setModalOpen(false);
            setModalQuery("");
          }}
          loading={loading}
          renderAction={
            renderRemoveAction
          }
        />
      )}
    </>
  );
}
