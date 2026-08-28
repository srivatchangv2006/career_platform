import { useEffect } from "react";

import UserMiniCard from "./UserMiniCard";

export default function NetworkPeopleModal({
  title,
  users,
  query,
  setQuery,
  onClose,
  loading,
  renderAction,
}) {
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [onClose]);

  return (
    <div
      className="network-modal-backdrop"
      onMouseDown={onClose}
    >
      <div
        className="network-modal"
        onMouseDown={(event) =>
          event.stopPropagation()
        }
      >
        <div className="network-modal-header">
          <div>
            <p className="eyebrow">
              MEDAI Network
            </p>

            <h2>{title}</h2>
          </div>

          <button
            type="button"
            className="network-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <input
          className="network-modal-search"
          type="search"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder={`Search ${title.toLowerCase()}...`}
          aria-label={`Search ${title}`}
        />

        <div className="network-modal-body">
          {loading && (
            <p className="network-muted">
              Loading...
            </p>
          )}

          {!loading &&
            users.length === 0 && (
              <p className="network-muted">
                No people found.
              </p>
            )}

          {!loading &&
            users.length > 0 && (
              <div className="network-modal-list">
                {users.map((user) => (
                  <div
                    key={user.user_id}
                    className="network-modal-person"
                  >
                    <UserMiniCard
                      user={user}
                    />

                    {renderAction &&
                      renderAction(user)}
                  </div>
                ))}
              </div>
            )}
        </div>
      </div>
    </div>
  );
}
