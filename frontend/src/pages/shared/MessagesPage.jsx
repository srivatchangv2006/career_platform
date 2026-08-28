import {
  useEffect,
  useState,
} from "react";

import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

import { useAuth } from "../../hooks/useAuth";

import {
  createOrGetConversation,
  deleteMessage,
  getMessages,
  getMyConversations,
  markConversationAsRead,
  sendMessage,
  updateMessage,
} from "../../api/messages.api";


function ConversationList({
  conversations,
  selectedId,
  onSelect,
}) {
  if (conversations.length === 0) {
    return (
      <div className="messages-empty">
        <h3>
          No conversations yet
        </h3>

        <p>
          Start a conversation from
          someone's profile.
        </p>
      </div>
    );
  }

  return (
    <div className="messages-conversation-list">
      {conversations.map(
        (conversation) => (
          <button
            key={conversation.id}
            type="button"
            className={`message-conversation ${
              selectedId ===
              conversation.id
                ? "message-conversation-active"
                : ""
            }`}
            onClick={() =>
              onSelect(
                conversation,
              )
            }
          >
            <div className="message-conversation-avatar">
              {conversation.other_user_avatar ? (
                <img
                  src={
                    conversation.other_user_avatar
                  }
                  alt={
                    conversation.other_user_name ||
                    conversation.other_user_email ||
                    "User"
                  }
                />
              ) : (
                (
                  conversation.other_user_name ||
                  conversation.other_user_email ||
                  "U"
                )
                  .charAt(0)
                  .toUpperCase()
              )}
            </div>

            <div className="message-conversation-body">
              <strong>
                {
                  conversation.other_user_name ||
                  conversation.other_user_email
                }
              </strong>

              <span className="message-conversation-subtitle">
                {conversation.other_user_company ||
                  conversation.other_user_headline ||
                  conversation.other_user_role ||
                  ""}
              </span>

              <span>
                {conversation.last_message ||
                  "No messages yet"}
              </span>
            </div>

            {conversation.unread_count >
              0 && (
              <span className="message-unread">
                {
                  conversation.unread_count
                }
              </span>
            )}
          </button>
        ),
      )}
    </div>
  );
}


function ChatWindow({
  conversation,
  messages,
  currentUserId,
  loading,
  onSend,
  onEdit,
  onDelete,
}) {
  const [draft, setDraft] =
    useState("");

  const [editingId, setEditingId] =
    useState("");

  const [editingText, setEditingText] =
    useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const content =
      draft.trim();

    if (!content) {
      return;
    }

    onSend(content);

    setDraft("");
  }

  if (!conversation) {
    return (
      <div className="messages-chat-empty">
        <div>
          <h2>
            Select a conversation
          </h2>

          <p>
            Choose someone from your
            conversations to start chatting.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="messages-chat">
      <div className="messages-chat-header">
        <div>
          <p className="eyebrow">
            Conversation
          </p>

          <div className="messages-chat-user">
            <div className="messages-chat-avatar">
              {conversation.other_user_avatar ? (
                <img
                  src={
                    conversation.other_user_avatar
                  }
                  alt={
                    conversation.other_user_name ||
                    "User"
                  }
                />
              ) : (
                (
                  conversation.other_user_name ||
                  conversation.other_user_email ||
                  "U"
                )
                  .charAt(0)
                  .toUpperCase()
              )}
            </div>

            <div>
              <h2>
                {
                  conversation.other_user_name ||
                  conversation.other_user_email
                }
              </h2>

              <span>
                {[
                  conversation.other_user_headline,
                  conversation.other_user_company,
                ]
                  .filter(Boolean)
                  .join(" · ") ||
                  conversation.other_user_role ||
                  ""}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="messages-history">
        {loading ? (
          <p className="jobs-muted">
            Loading messages...
          </p>
        ) : messages.length === 0 ? (
          <div className="messages-empty">
            <h3>
              No messages yet
            </h3>

            <p>
              Send the first message.
            </p>
          </div>
        ) : (
          messages.map((message) => {
            const own =
              String(
                message.sender_id,
              ) ===
              String(currentUserId);

            const editing =
              editingId ===
              message.id;

            return (
              <div
                key={message.id}
                className={`message-row ${
                  own
                    ? "message-row-own"
                    : "message-row-other"
                }`}
              >
                {editing ? (
                  <div className="message-edit-box">
                    <textarea
                      value={
                        editingText
                      }
                      onChange={(event) =>
                        setEditingText(
                          event.target
                            .value,
                        )
                      }
                      autoFocus
                    />

                    <div>
                      <Button
                        type="button"
                        onClick={() => {
                          onEdit(
                            message.id,
                            editingText,
                          );

                          setEditingId("");
                          setEditingText("");
                        }}
                      >
                        Save
                      </Button>

                      <Button
                        type="button"
                        variant="ghost"
                        onClick={() => {
                          setEditingId("");
                          setEditingText("");
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="message-bubble-wrapper">
                    <div
                      className={`message-bubble ${
                        own
                          ? "message-bubble-own"
                          : "message-bubble-other"
                      }`}
                    >
                      {message.content}
                    </div>

                    <div className="message-meta">
                      <time>
                        {message.created_at
                          ? new Date(
                              message.created_at,
                            ).toLocaleString()
                          : ""}
                      </time>

                      {own && (
                        <div className="message-actions">
                          <button
                            type="button"
                            onClick={() => {
                              setEditingId(
                                message.id,
                              );

                              setEditingText(
                                message.content,
                              );
                            }}
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              onDelete(
                                message.id,
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <form
        className="message-compose"
        onSubmit={handleSubmit}
      >
        <input
          value={draft}
          onChange={(event) =>
            setDraft(
              event.target.value,
            )
          }
          placeholder="Write a message..."
        />

        <Button
          type="submit"
          disabled={!draft.trim()}
        >
          Send
        </Button>
      </form>
    </div>
  );
}


export default function MessagesPage() {
  const { user } =
    useAuth();

  const [conversations, setConversations] =
    useState([]);

  const [selectedConversation, setSelectedConversation] =
    useState(null);

  const [messages, setMessages] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [loadingMessages, setLoadingMessages] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const result =
          await getMyConversations();

        if (active) {
          setConversations(
            Array.isArray(result)
              ? result
              : [],
          );
        }
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data
              ?.detail ||
              "Unable to load messages.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      active = false;
    };
  }, []);


  useEffect(() => {
    let active = true;

    async function refreshConversations() {
      try {
        const result =
          await getMyConversations();

        if (!active) {
          return;
        }

        const refreshed =
          Array.isArray(result)
            ? result
            : [];

        setConversations(
          refreshed.map(
            (conversation) =>
              selectedConversation?.id ===
              conversation.id
                ? {
                    ...conversation,
                    unread_count: 0,
                  }
                : conversation,
          ),
        );
      } catch {
        // Background refresh failures should not
        // interrupt an active conversation.
      }
    }

    const intervalId = window.setInterval(
      refreshConversations,
      5000,
    );

    return () => {
      active = false;
      window.clearInterval(
        intervalId,
      );
    };
  }, [selectedConversation?.id]);

  async function openConversation(
    conversation,
  ) {
    setSelectedConversation(
      conversation,
    );

    setLoadingMessages(true);
    setError("");

    try {
      const result =
        await getMessages(
          conversation.id,
        );

      setMessages(
        Array.isArray(result)
          ? result
          : [],
      );

      await markConversationAsRead(
        conversation.id,
      );

      setConversations(
        (current) =>
          current.map(
            (item) =>
              item.id ===
              conversation.id
                ? {
                    ...item,
                    unread_count: 0,
                  }
                : item,
          ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to load conversation.",
      );
    } finally {
      setLoadingMessages(false);
    }
  }

  useEffect(() => {
    const conversationId =
      selectedConversation?.id;

    if (!conversationId) {
      return undefined;
    }

    let active = true;

    async function refreshOpenConversation() {
      try {
        const result =
          await getMessages(
            conversationId,
          );

        if (!active) {
          return;
        }

        setMessages(
          Array.isArray(result)
            ? result
            : [],
        );

        await markConversationAsRead(
          conversationId,
        );

        if (!active) {
          return;
        }

        setConversations(
          (current) =>
            current.map(
              (conversation) =>
                conversation.id ===
                conversationId
                  ? {
                      ...conversation,
                      unread_count: 0,
                    }
                  : conversation,
            ),
        );
      } catch {
        // Ignore background refresh errors.
      }
    }

    const intervalId =
      window.setInterval(
        refreshOpenConversation,
        5000,
      );

    return () => {
      active = false;
      window.clearInterval(
        intervalId,
      );
    };
  }, [
    selectedConversation?.id,
  ]);

  async function handleSend(
    content,
  ) {
    if (!selectedConversation) {
      return;
    }

    try {
      const result =
        await sendMessage(
          selectedConversation.id,
          content,
        );

      setMessages(
        (current) => [
          ...current,
          result,
        ],
      );

      setConversations((current) => {
        const updatedConversation = {
          ...selectedConversation,
          last_message:
            result.content,
          last_message_at:
            result.created_at,
          updated_at:
            result.created_at,
          unread_count: 0,
        };

        const remaining =
          current.filter(
            (conversation) =>
              conversation.id !==
              selectedConversation.id,
          );

        return [
          updatedConversation,
          ...remaining,
        ];
      });

      setSelectedConversation(
        (current) =>
          current
            ? {
                ...current,
                last_message:
                  result.content,
                last_message_at:
                  result.created_at,
                updated_at:
                  result.created_at,
                unread_count: 0,
              }
            : current,
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to send message.",
      );
    }
  }

  async function handleEdit(
    messageId,
    content,
  ) {
    if (!content.trim()) {
      return;
    }

    try {
      const updated =
        await updateMessage(
          messageId,
          content,
        );

      setMessages(
        (current) =>
          current.map(
            (message) =>
              message.id ===
              messageId
                ? updated
                : message,
          ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to edit message.",
      );
    }
  }

  async function handleDelete(
    messageId,
  ) {
    try {
      await deleteMessage(
        messageId,
      );

      setMessages(
        (current) =>
          current.filter(
            (message) =>
              message.id !==
              messageId,
          ),
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to delete message.",
      );
    }
  }

  /*
   * Support /messages?user=<user_id>
   * from public profiles.
   *
   * We intentionally don't use the URL parameter
   * until the initial conversation list has loaded,
   * because the conversation has to be created/found
   * through the protected backend endpoint.
   */
  useEffect(() => {
    let active = true;

    async function openUserFromQuery() {
      const params =
        new URLSearchParams(
          window.location.search,
        );

      const userId =
        params.get("user");

      if (!userId) {
        return;
      }

      try {
        const conversation =
          await createOrGetConversation(
            userId,
          );

        if (!active) {
          return;
        }

        const conversationSummary = {
          ...conversation,
          unread_count: 0,
          last_message:
            null,
          last_message_at:
            null,
          updated_at:
            conversation.updated_at ||
            conversation.created_at ||
            new Date().toISOString(),
        };

        setConversations(
          (current) => {
            const exists =
              current.some(
                (item) =>
                  item.id ===
                  conversation.id,
              );

            if (exists) {
              return current.map(
                (item) =>
                  item.id ===
                  conversation.id
                    ? {
                        ...item,
                        ...conversationSummary,
                      }
                    : item,
              );
            }

            return [
              conversationSummary,
              ...current,
            ];
          },
        );

        await openConversation(
          conversationSummary,
        );
      } catch (err) {
        if (active) {
          setError(
            err?.response?.data
              ?.detail ||
              "Unable to start conversation.",
          );
        }
      }
    }

    openUserFromQuery();

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="messages-page">
      <div className="messages-hero">
        <p className="eyebrow">
          MEDAI
        </p>

        <h1>
          Messages
        </h1>

        <p>
          Chat directly with other MEDAI
          users.
        </p>
      </div>

      {error && (
        <div className="message-error">
          {error}
        </div>
      )}

      <div className="messages-layout">
        <Card className="messages-sidebar">
          <div className="messages-sidebar-header">
            <div>
              <p className="eyebrow">
                Inbox
              </p>

              <h2>
                Conversations
              </h2>
            </div>
          </div>

          {loading ? (
            <p className="jobs-muted">
              Loading conversations...
            </p>
          ) : (
            <ConversationList
              conversations={
                conversations
              }
              selectedId={
                selectedConversation?.id
              }
              onSelect={
                openConversation
              }
            />
          )}
        </Card>

        <Card className="messages-chat-card">
          <ChatWindow
            conversation={
              selectedConversation
            }
            messages={messages}
            currentUserId={
              user?.id
            }
            loading={
              loadingMessages
            }
            onSend={
              handleSend
            }
            onEdit={
              handleEdit
            }
            onDelete={
              handleDelete
            }
          />
        </Card>
      </div>
    </section>
  );
}
