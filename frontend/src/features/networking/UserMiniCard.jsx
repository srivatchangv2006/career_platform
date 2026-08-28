import { Link } from "react-router-dom";

import Avatar from "../../components/ui/Avatar";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";

export default function UserMiniCard({
  user,
  actionLabel,
  onAction,
  actionDisabled = false,
}) {
  if (!user || !user.user_id) {
    return null;
  }

  const name =
    user.display_name ||
    "MEDAI User";

  const handle =
    user.handle ||
    "";

  const headline =
    user.headline ||
    "";

  return (
    <Card className="network-user-card">
      <div className="network-user-content">
        <Link
          to={`/profile/${user.user_id}`}
          className="network-user-main"
          aria-label={`View ${name}'s profile`}
        >
          <Avatar
            name={name}
            src={
              user.profile_image_blob_path ||
              null
            }
            size="medium"
          />

          <div className="network-user-info">
            <span className="network-user-name">
              {name}
            </span>

            {handle && (
              <span className="network-user-handle">
                {handle}
              </span>
            )}

            {headline && (
              <p>{headline}</p>
            )}

            <span className="network-user-role">
              {user.role}
            </span>

            {user.company_name && (
              <span className="network-user-company">
                {user.company_name}
              </span>
            )}
          </div>
        </Link>

        {actionLabel && onAction && (
          <Button
            variant="secondary"
            disabled={actionDisabled}
            onClick={onAction}
          >
            {actionLabel}
          </Button>
        )}
      </div>
    </Card>
  );
}
