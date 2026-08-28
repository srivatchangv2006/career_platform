import {
  useEffect,
  useState,
} from "react";

import Avatar from "../../components/ui/Avatar";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import { useAuth } from "../../hooks/useAuth";

import {
  createCommunityComment,
  deleteCommunityComment,
  deleteCommunityPost,
  getCommunityComments,
  getCommunityImageBlob,
  getCommunityPostImages,
  removeCommunityPostVote,
  updateCommunityComment,
  voteCommunityPost,
} from "../../api/community.api";


function CommentItem({
  comment,
  depth = 0,
  user,
  comments,
  onReply,
  onEdit,
  onDelete,
  editingCommentId,
  editingCommentText,
  setEditingCommentText,
  onSaveEdit,
  onCancelEdit,
}) {
  const author =
    comment.author || {};

  const authorName =
    author.display_name ||
    "Community member";

  const isOwner =
    String(comment.user_id) ===
    String(user?.id);

  const children =
    comments.filter(
      (child) =>
        String(
          child.parent_comment_id,
        ) ===
        String(comment.id),
    );

  const indentation =
    Math.min(depth, 6) * 28;

  return (
    <div
      className="community-comment-thread"
      style={{
        marginLeft: `${indentation}px`,
      }}
    >
      <div className="community-comment">
        {editingCommentId ===
        comment.id ? (
          <div className="community-comment-edit">
            <input
              value={
                editingCommentText
              }
              onChange={(event) =>
                setEditingCommentText(
                  event.target.value,
                )
              }
            />

            <div className="community-comment-edit-actions">
              <Button
                type="button"
                onClick={() =>
                  onSaveEdit(
                    comment.id,
                  )
                }
              >
                Save
              </Button>

              <Button
                type="button"
                variant="ghost"
                onClick={onCancelEdit}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="community-comment-author">
              <Avatar
                name={authorName}
                src={
                  author.profile_image_blob_path ||
                  null
                }
                size="small"
              />

              <div>
                <strong>
                  {authorName}
                </strong>

                <span>
                  {author.role ===
                  "RECRUITER"
                    ? [
                        author.designation,
                        author.company_name,
                      ]
                        .filter(Boolean)
                        .join(" · ") ||
                      "Recruiter"
                    : author.headline ||
                      "Community member"}
                </span>
              </div>
            </div>

            <p>
              {comment.content}
            </p>

            <time>
              {comment.created_at
                ? new Date(
                    comment.created_at,
                  ).toLocaleString()
                : ""}
            </time>

            <div className="community-comment-actions">
              <button
                type="button"
                onClick={() =>
                  onReply(comment.id)
                }
              >
                Reply
              </button>

              {isOwner && (
                <>
                  <button
                    type="button"
                    onClick={() =>
                      onEdit(
                        comment,
                      )
                    }
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      onDelete(
                        comment.id,
                      )
                    }
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </>
        )}
      </div>

      {children.map(
        (child) => (
          <CommentItem
            key={child.id}
            comment={child}
            depth={depth + 1}
            user={user}
            comments={comments}
            onReply={onReply}
            onEdit={onEdit}
            onDelete={onDelete}
            editingCommentId={
              editingCommentId
            }
            editingCommentText={
              editingCommentText
            }
            setEditingCommentText={
              setEditingCommentText
            }
            onSaveEdit={
              onSaveEdit
            }
            onCancelEdit={
              onCancelEdit
            }
          />
        ),
      )}
    </div>
  );
}


export default function PostCard({
  post,
  onDeleted,
}) {
  const { user } =
    useAuth();

  const [images, setImages] =
    useState([]);

  const [comments, setComments] =
    useState([]);

  const [showComments, setShowComments] =
    useState(false);

  const [commentText, setCommentText] =
    useState("");

  const [replyToCommentId, setReplyToCommentId] =
    useState("");

  const [replyText, setReplyText] =
    useState("");

  const [loadingImages, setLoadingImages] =
    useState(false);

  const [loadingComments, setLoadingComments] =
    useState(false);

  const [submittingComment, setSubmittingComment] =
    useState(false);

  const [submittingReply, setSubmittingReply] =
    useState(false);

  const [voting, setVoting] =
    useState(false);

  const [deleting, setDeleting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [commentError, setCommentError] =
    useState("");

  const [editingCommentId, setEditingCommentId] =
    useState("");

  const [editingCommentText, setEditingCommentText] =
    useState("");

  const [voteState, setVoteState] =
    useState({
      upvotes:
        post.upvotes || 0,
      downvotes:
        post.downvotes || 0,
      userVote:
        post.user_vote || null,
    });

  useEffect(() => {
    let active = true;
    const objectUrls = [];

    async function loadImages() {
      setLoadingImages(true);

      try {
        const metadata =
          await getCommunityPostImages(
            post.id,
          );

        const loaded =
          await Promise.all(
            (Array.isArray(metadata)
              ? metadata
              : []
            ).map(async (image) => {
              const blob =
                await getCommunityImageBlob(
                  post.id,
                  image.id,
                );

              const url =
                URL.createObjectURL(
                  blob,
                );

              objectUrls.push(url);

              return {
                ...image,
                url,
              };
            }),
          );

        if (active) {
          setImages(
            loaded,
          );
        }
      } catch {
        if (active) {
          setImages([]);
        }
      } finally {
        if (active) {
          setLoadingImages(false);
        }
      }
    }

    loadImages();

    return () => {
      active = false;

      objectUrls.forEach(
        (url) =>
          URL.revokeObjectURL(
            url,
          ),
      );
    };
  }, [post.id]);

  async function loadComments() {
    setLoadingComments(true);
    setCommentError("");

    try {
      const result =
        await getCommunityComments(
          post.id,
        );

      setComments(
        Array.isArray(result)
          ? result
          : [],
      );
    } catch (err) {
      setCommentError(
        err?.response?.data?.detail ||
          "Unable to load comments.",
      );
    } finally {
      setLoadingComments(false);
    }
  }

  async function handleToggleComments() {
    const next =
      !showComments;

    setShowComments(next);

    if (
      next &&
      comments.length === 0
    ) {
      await loadComments();
    }
  }

  async function handleCommentSubmit(
    event,
  ) {
    event.preventDefault();

    if (!commentText.trim()) {
      return;
    }

    setSubmittingComment(true);
    setCommentError("");

    try {
      const comment =
        await createCommunityComment(
          post.id,
          {
            content:
              commentText.trim(),
            parent_comment_id:
              null,
          },
        );

      setComments((current) => [
        ...current,
        comment,
      ]);

      setCommentText("");
      setShowComments(true);
    } catch (err) {
      setCommentError(
        err?.response?.data?.detail ||
          "Unable to add comment.",
      );
    } finally {
      setSubmittingComment(false);
    }
  }

  async function handleReplySubmit(
    event,
  ) {
    event.preventDefault();

    if (
      !replyToCommentId ||
      !replyText.trim()
    ) {
      return;
    }

    setSubmittingReply(true);
    setCommentError("");

    try {
      const reply =
        await createCommunityComment(
          post.id,
          {
            content:
              replyText.trim(),
            parent_comment_id:
              replyToCommentId,
          },
        );

      setComments((current) => [
        ...current,
        reply,
      ]);

      setReplyText("");
      setReplyToCommentId("");
      setShowComments(true);
    } catch (err) {
      setCommentError(
        err?.response?.data?.detail ||
          "Unable to add reply.",
      );
    } finally {
      setSubmittingReply(false);
    }
  }

  async function handleVote() {
    setVoting(true);
    setError("");

    try {
      if (
        voteState.userVote ===
        "UP"
      ) {
        await removeCommunityPostVote(
          post.id,
        );

        setVoteState((current) => ({
          ...current,
          upvotes: Math.max(
            0,
            current.upvotes - 1,
          ),
          userVote: null,
        }));
      } else {
        await voteCommunityPost(
          post.id,
          "UP",
        );

        setVoteState((current) => ({
          upvotes:
            current.upvotes + 1,
          downvotes:
            current.userVote ===
            "DOWN"
              ? Math.max(
                  0,
                  current.downvotes - 1,
                )
              : current.downvotes,
          userVote: "UP",
        }));
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update your vote.",
      );
    } finally {
      setVoting(false);
    }
  }

  async function handleDeletePost() {
    setDeleting(true);
    setError("");

    try {
      await deleteCommunityPost(
        post.id,
      );

      onDeleted(post.id);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to delete this post.",
      );
    } finally {
      setDeleting(false);
    }
  }

  async function handleSaveComment(
    commentId,
  ) {
    if (
      !editingCommentText.trim()
    ) {
      return;
    }

    try {
      const updated =
        await updateCommunityComment(
          commentId,
          {
            content:
              editingCommentText.trim(),
          },
        );

      setComments((current) =>
        current.map(
          (comment) =>
            comment.id ===
            commentId
              ? updated
              : comment,
        ),
      );

      setEditingCommentId("");
      setEditingCommentText("");
    } catch (err) {
      setCommentError(
        err?.response?.data?.detail ||
          "Unable to update comment.",
      );
    }
  }

  async function handleDeleteComment(
    commentId,
  ) {
    try {
      await deleteCommunityComment(
        commentId,
      );

      setComments((current) =>
        current.filter(
          (comment) =>
            comment.id !==
            commentId,
        ),
      );
    } catch (err) {
      setCommentError(
        err?.response?.data?.detail ||
          "Unable to delete comment.",
      );
    }
  }

  const author =
    post.author || {};

  const authorName =
    author.display_name ||
    "MEDAI User";

  const authorRole =
    author.role === "RECRUITER"
      ? [
          author.designation,
          author.company_name,
        ]
          .filter(Boolean)
          .join(" · ") ||
        "Recruiter"
      : author.headline ||
        "Community member";

  const isOwner =
    String(post.user_id) ===
    String(user?.id);

  const topLevelComments =
    comments.filter(
      (comment) =>
        !comment.parent_comment_id,
    );

  return (
    <Card className="community-post-card">
      <div className="community-post-header">
        <Avatar
          name={authorName}
          src={
            author.profile_image_blob_path ||
            null
          }
          size="medium"
        />

        <div className="community-post-author">
          <strong>
            {authorName}
          </strong>

          <p>
            {authorRole}
          </p>

          <time>
            {post.created_at
              ? new Date(
                  post.created_at,
                ).toLocaleString()
              : ""}
          </time>
        </div>

        {isOwner && (
          <Button
            variant="ghost"
            disabled={deleting}
            onClick={
              handleDeletePost
            }
          >
            {deleting
              ? "Deleting..."
              : "Delete"}
          </Button>
        )}
      </div>

      <div className="community-post-content">
        <h2>
          {post.title}
        </h2>

        <p>
          {post.content}
        </p>
      </div>

      {loadingImages && (
        <p className="post-image-loading">
          Loading images...
        </p>
      )}

      {images.length > 0 && (
        <div
          className={
            images.length === 1
              ? "post-images post-images-single"
              : "post-images"
          }
        >
          {images.map((image) => (
            <img
              key={image.id}
              src={image.url}
              alt={image.file_name}
              className="post-image"
            />
          ))}
        </div>
      )}

      {error && (
        <div className="community-message">
          {error}
        </div>
      )}

      <div className="community-post-actions">
        <button
          type="button"
          disabled={voting}
          className={
            voteState.userVote ===
            "UP"
              ? "community-vote-active"
              : ""
          }
          onClick={handleVote}
        >
          ↑ {voteState.upvotes}
        </button>

        <button
          type="button"
          onClick={
            handleToggleComments
          }
        >
          💬{" "}
          {showComments
            ? "Hide comments"
            : "Comments"}
        </button>

        {voteState.downvotes >
          0 && (
          <span className="community-vote-down-count">
            ↓{" "}
            {voteState.downvotes}
          </span>
        )}
      </div>

      <form
        className="community-comment-form"
        onSubmit={
          handleCommentSubmit
        }
      >
        <input
          value={commentText}
          onChange={(event) =>
            setCommentText(
              event.target.value,
            )
          }
          placeholder="Write a comment..."
        />

        <Button
          type="submit"
          variant="secondary"
          disabled={
            submittingComment ||
            !commentText.trim()
          }
        >
          {submittingComment
            ? "Posting..."
            : "Comment"}
        </Button>
      </form>

      {showComments && (
        <div className="community-comments">
          {commentError && (
            <div className="community-message">
              {commentError}
            </div>
          )}

          {loadingComments ? (
            <p className="jobs-muted">
              Loading comments...
            </p>
          ) : comments.length ===
            0 ? (
            <p className="jobs-muted">
              No comments yet.
            </p>
          ) : (
            <>
              {replyToCommentId && (
                <form
                  className="community-reply-form"
                  onSubmit={
                    handleReplySubmit
                  }
                >
                  <div className="community-reply-label">
                    Replying to a comment
                  </div>

                  <div className="community-reply-input-row">
                    <input
                      value={replyText}
                      onChange={(event) =>
                        setReplyText(
                          event.target.value,
                        )
                      }
                      placeholder="Write your reply..."
                      autoFocus
                    />

                    <Button
                      type="submit"
                      variant="secondary"
                      disabled={
                        submittingReply ||
                        !replyText.trim()
                      }
                    >
                      {submittingReply
                        ? "Replying..."
                        : "Reply"}
                    </Button>

                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setReplyToCommentId("");
                        setReplyText("");
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              )}

              <div className="community-comment-tree">
                {topLevelComments.map(
                  (comment) => (
                    <CommentItem
                      key={comment.id}
                      comment={comment}
                      depth={0}
                      user={user}
                      comments={comments}
                      onReply={(
                        commentId,
                      ) => {
                        setReplyToCommentId(
                          commentId,
                        );

                        setReplyText("");
                      }}
                      onEdit={(
                        commentToEdit,
                      ) => {
                        setEditingCommentId(
                          commentToEdit.id,
                        );

                        setEditingCommentText(
                          commentToEdit.content,
                        );
                      }}
                      onDelete={
                        handleDeleteComment
                      }
                      editingCommentId={
                        editingCommentId
                      }
                      editingCommentText={
                        editingCommentText
                      }
                      setEditingCommentText={
                        setEditingCommentText
                      }
                      onSaveEdit={
                        handleSaveComment
                      }
                      onCancelEdit={() => {
                        setEditingCommentId("");
                        setEditingCommentText("");
                      }}
                    />
                  ),
                )}
              </div>
            </>
          )}
        </div>
      )}
    </Card>
  );
}
