import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import {
  getCommunityPosts,
} from "../../api/community.api";

import CreatePost from "../../features/community/CreatePost";
import PostCard from "../../features/community/PostCard";

export default function CommunityPage() {
  const [posts, setPosts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showCreatePost, setShowCreatePost] =
    useState(false);

  const loadPosts =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const result =
          await getCommunityPosts();

        setPosts(
          Array.isArray(result)
            ? result
            : [],
        );
      } catch (err) {
        setPosts([]);

        setError(
          err?.response?.data?.detail ||
            "Unable to load the community.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    // Load community feed.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadPosts();
  }, [loadPosts]);

  function handleCreated(post) {
    setPosts((current) => [
      post,
      ...current,
    ]);

    setShowCreatePost(false);
  }

  function handleDeleted(postId) {
    setPosts((current) =>
      current.filter(
        (post) =>
          post.id !== postId,
      ),
    );
  }

  return (
    <section className="community-page">
      <div className="community-hero">
        <p className="eyebrow">
          MEDAI
        </p>

        <h1>
          Community
        </h1>

        <p>
          Share, connect, and learn from
          the MEDAI community.
        </p>
      </div>

      {error && (
        <div className="community-message">
          {error}
        </div>
      )}

      <Card className="community-feed-card">
        <div className="community-feed-header">
          <div>
            <p className="eyebrow">
              Community feed
            </p>

            <h2>
              Latest posts
            </h2>
          </div>

          <div className="community-feed-header-actions">
            <span className="community-post-count">
              {posts.length}
            </span>

            <Button
              onClick={() =>
                setShowCreatePost(true)
              }
            >
              + Create post
            </Button>
          </div>
        </div>

        {loading && (
          <p className="jobs-muted">
            Loading community posts...
          </p>
        )}

        {!loading &&
          posts.length === 0 && (
            <div className="community-empty">
              <h3>
                No posts yet
              </h3>

              <p>
                Be the first person to
                start a conversation.
              </p>

              <Button
                onClick={() =>
                  setShowCreatePost(true)
                }
              >
                Create the first post
              </Button>
            </div>
          )}

        {!loading &&
          posts.length > 0 && (
            <div className="community-feed">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onDeleted={
                    handleDeleted
                  }
                />
              ))}
            </div>
          )}
      </Card>

      {showCreatePost && (
        <div
          className="community-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              setShowCreatePost(false);
            }
          }}
        >
          <div
            className="community-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-post-title"
          >
            <button
              type="button"
              className="community-modal-close"
              onClick={() =>
                setShowCreatePost(false)
              }
              aria-label="Close create post"
            >
              ×
            </button>

            <CreatePost
              onCreated={
                handleCreated
              }
            />
          </div>
        </div>
      )}
    </section>
  );
}
