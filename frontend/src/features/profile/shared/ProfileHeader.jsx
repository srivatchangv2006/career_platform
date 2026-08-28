import Avatar from "../../../components/ui/Avatar";
import Badge from "../../../components/ui/Badge";
import Button from "../../../components/ui/Button";
import Card from "../../../components/ui/Card";

import { getDisplayHandle } from "../../../utils/getDisplayHandle";

import ProfileActions from "../public/ProfileActions";

export default function ProfileHeader({
  profile,
  email,
  role,
  isOwnProfile = false,
  onEdit,
}) {
  const displayName =
    profile?.full_name ||
    profile?.designation ||
    email?.split("@")[0] ||
    "MEDAI User";

  const handle =
    getDisplayHandle(email);

  const headline =
    profile?.headline ||
    profile?.designation ||
    "";

  const image =
    profile?.profile_image_blob_path ||
    null;

  return (
    <Card className="profile-header-card">
      <div className="profile-header-cover" />

      <div className="profile-header-content">
        <Avatar
          name={displayName}
          src={image}
          size="large"
        />

        <div className="profile-header-main">
          <div className="profile-header-title-row">
            <div>
              <h1>
                {displayName}
              </h1>

              <span className="profile-handle">
                {handle}
              </span>
            </div>

            <Badge>
              {role}
            </Badge>
          </div>

          {headline && (
            <p className="profile-headline">
              {headline}
            </p>
          )}

          {profile?.location && (
            <p className="profile-location">
              {profile.location}
            </p>
          )}

          {profile?.company_name && (
            <p className="profile-company">
              {profile.company_name}
            </p>
          )}

          {isOwnProfile ? (
            <div className="profile-actions">
              <Button
                variant="secondary"
                onClick={onEdit}
              >
                Edit Profile
              </Button>
            </div>
          ) : (
            <ProfileActions
              userId={profile?.user_id}
              isOwnProfile={false}
            />
          )}
        </div>
      </div>
    </Card>
  );
}
