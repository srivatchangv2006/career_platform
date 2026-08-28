import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import Card from "../../../components/ui/Card";

import {
  getPublicProfile,
} from "../../../api/profile.api";

import ProfileHeader from "../shared/ProfileHeader";
import ProfileAbout from "../shared/ProfileAbout";

import { useAuth } from "../../../hooks/useAuth";

export default function PublicProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();

  const { user } = useAuth();

  const [profile, setProfile] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      setLoading(true);
      setError("");

      try {
        const result =
          await getPublicProfile(userId);

        if (active) {
          setProfile(result);
        }
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              "Unable to load profile.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadProfile();

    return () => {
      active = false;
    };
  }, [userId]);

  if (loading) {
    return (
      <div className="page-loading">
        Loading profile...
      </div>
    );
  }

  if (error) {
    return (
      <Card className="feed-state feed-error">
        {error}
      </Card>
    );
  }

  if (!profile) {
    return null;
  }

  const isOwnProfile =
    profile.user_id === user?.id;

  function handleMessage() {
    navigate(
      `/messages?user=${profile.user_id}`,
    );
  }

  return (
    <section className="profile-page">
      <ProfileHeader
        profile={profile}
        email={profile.email}
        role={profile.role}
        isOwnProfile={isOwnProfile}
        onMessage={handleMessage}
      />

      <ProfileAbout
        profile={profile}
      />

      {profile.company && (
        <Card className="profile-section-card">
          <p className="eyebrow">
            Company
          </p>

          <h2>
            {profile.company.name}
          </h2>

          <p className="profile-bio">
            {profile.company.description ||
              "No company description available."}
          </p>
        </Card>
      )}

      <Card className="profile-section-card">
        <div className="profile-section-header">
          <div>
            <p className="eyebrow">
              Community
            </p>

            <h2>
              Posts
            </h2>
          </div>

          <span className="profile-post-count">
            {profile.posts?.length || 0}
          </span>
        </div>

        {profile.posts?.length ? (
          <div className="profile-post-list">
            {profile.posts.map((post) => (
              <article
                key={post.id}
                className="profile-post-item"
              >
                <h3>
                  {post.title}
                </h3>

                <p>
                  {post.content}
                </p>
              </article>
            ))}
          </div>
        ) : (
          <p className="profile-empty-text">
            No community posts yet.
          </p>
        )}
      </Card>
    </section>
  );
}
