import { useAuth } from "../../hooks/useAuth";

import Card from "../../components/ui/Card";

import ConnectionRequests from "./ConnectionRequests";
import MyConnections from "./MyConnections";
import FollowingList from "./FollowingList";
import FollowersList from "./FollowersList";

export default function NetworkPage() {
  const { user } = useAuth();

  return (
    <section className="network-page">
      <div className="network-hero">
        <div>
          <p className="eyebrow">
            MEDAI Network
          </p>

          <h1>
            Your professional network
          </h1>

          <p>
            Manage your connections,
            followers, and the people you
            follow. Select any person to
            open their MEDAI profile.
          </p>
        </div>
      </div>

      <div className="network-sections">
        <ConnectionRequests />

        <MyConnections
          currentUserId={user?.id}
        />

        <FollowingList />

        {user?.id && (
          <FollowersList
            userId={user.id}
          />
        )}
      </div>

      <Card className="network-info-card network-bottom-info">
        <p className="eyebrow">
          Discover people
        </p>

        <h2>
          Find someone on MEDAI
        </h2>

        <p>
          Use the search bar in the top
          navigation to find another
          candidate or recruiter. Open
          their profile to follow, connect,
          or message them.
        </p>
      </Card>
    </section>
  );
}
