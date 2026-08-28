import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "../../../components/ui/Button";

import {
  createConnection,
  followUser,
  getMyConnections,
  getMyFollowing,
  unfollowUser,
} from "../../../api/networking.api";

export default function ProfileActions({
  userId,
  isOwnProfile = false,
}) {
  const navigate = useNavigate();

  const [following, setFollowing] =
    useState(false);

  const [connectionStatus, setConnectionStatus] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState(false);

  useEffect(() => {
    let active = true;

    async function loadRelationshipState() {
      if (isOwnProfile) {
        setLoading(false);
        return;
      }

      try {
        const [
          followingResult,
          connectionsResult,
        ] = await Promise.all([
          getMyFollowing(),
          getMyConnections(),
        ]);

        if (!active) {
          return;
        }

        const isFollowing =
          followingResult.some(
            (item) =>
              item.following_id === userId,
          );

        const connection =
          connectionsResult.find(
            (item) =>
              item.requester_id === userId ||
              item.receiver_id === userId,
          );

        setFollowing(isFollowing);

        if (connection) {
          const status =
            connection.status?.value ||
            connection.status;

          setConnectionStatus(status);
        } else {
          setConnectionStatus(null);
        }
      } catch {
        if (active) {
          setFollowing(false);
          setConnectionStatus(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadRelationshipState();

    return () => {
      active = false;
    };
  }, [userId, isOwnProfile]);

  async function handleFollow() {
    setActionLoading(true);

    try {
      if (following) {
        await unfollowUser(userId);
        setFollowing(false);
      } else {
        await followUser(userId);
        setFollowing(true);
      }
    } finally {
      setActionLoading(false);
    }
  }

  async function handleConnect() {
    setActionLoading(true);

    try {
      const result =
        await createConnection(userId);

      const status =
        result.status?.value ||
        result.status ||
        "PENDING";

      setConnectionStatus(status);
    } finally {
      setActionLoading(false);
    }
  }

  function handleMessage() {
    navigate(
      `/messages?user=${encodeURIComponent(
        userId,
      )}`,
    );
  }

  if (loading) {
    return (
      <div className="profile-actions">
        <Button
          variant="secondary"
          disabled
        >
          Loading...
        </Button>
      </div>
    );
  }

  if (isOwnProfile) {
    return null;
  }

  return (
    <div className="profile-actions">
      <Button
        variant="secondary"
        disabled={actionLoading}
        onClick={handleFollow}
      >
        {following
          ? "Following"
          : "Follow"}
      </Button>

      <Button
        variant="secondary"
        disabled={
          actionLoading ||
          connectionStatus !== null
        }
        onClick={handleConnect}
      >
        {connectionStatus === "ACCEPTED"
          ? "Connected"
          : connectionStatus === "PENDING"
            ? "Pending"
            : connectionStatus ===
                "REJECTED"
              ? "Connect"
              : "Connect"}
      </Button>

      <Button
        disabled={actionLoading}
        onClick={handleMessage}
      >
        Message
      </Button>
    </div>
  );
}
