import Card from "../../../components/ui/Card";

export default function ProfileAbout({
  profile,
}) {
  if (!profile?.bio) {
    return (
      <Card className="profile-section-card">
        <h2>About</h2>

        <p className="profile-empty-text">
          No bio has been added yet.
        </p>
      </Card>
    );
  }

  return (
    <Card className="profile-section-card">
      <h2>About</h2>

      <p className="profile-bio">
        {profile.bio}
      </p>
    </Card>
  );
}
