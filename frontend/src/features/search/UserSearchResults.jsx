import { Link } from "react-router-dom";

import Avatar from "../../components/ui/Avatar";
import Card from "../../components/ui/Card";

export default function UserSearchResults({
  results,
  loading,
  query,
  onSelect,
}) {
  if (!query || query.length < 2) {
    return null;
  }

  return (
    <Card className="search-results-panel">
      {loading && (
        <div className="search-state">
          Searching...
        </div>
      )}

      {!loading &&
        results.length === 0 && (
          <div className="search-state">
            No people found.
          </div>
        )}

      {!loading &&
        results.length > 0 &&
        results.map((user) => (
          <Link
            key={user.id}
            to={`/profile/${user.id}`}
            className="search-result"
            onClick={onSelect}
          >
            <Avatar
              name={user.display_name}
              src={
                user.profile_image_blob_path ||
                null
              }
              size="medium"
            />

            <div className="search-result-info">
              <strong>
                {user.display_name}
              </strong>

              <span>
                {user.handle}
              </span>

              <p>
                {user.headline ||
                  user.role}
              </p>
            </div>

            <span className="search-result-role">
              {user.role}
            </span>
          </Link>
        ))}
    </Card>
  );
}
