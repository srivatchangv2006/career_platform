import { useEffect, useState } from "react";

import Card from "../../components/ui/Card";
import PostCard from "../community/PostCard";
import { getCommunityPosts } from "../../api/community.api";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPosts() {
      setLoading(true);
      setError("");

      try {
        const result = await getCommunityPosts();

        if (active) {
          setPosts(result);
        }
      } catch {
        if (active) {
          setError(
            "Unable to load the community feed.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadPosts();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <Card className="feed-state">
        Loading your feed...
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="feed-state feed-error">
        {error}
      </Card>
    );
  }

  if (posts.length === 0) {
    return (
      <Card className="feed-state">
        No posts yet. Be the first to
        share something with the MEDAI
        community.
      </Card>
    );
  }

  return (
    <div className="feed">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
        />
      ))}
    </div>
  );
}
