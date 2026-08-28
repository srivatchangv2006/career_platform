import apiClient from "./client";


export async function getMyConversations() {
  const response =
    await apiClient.get(
      "/messages/conversations",
    );

  return response.data;
}


export async function getConversation(
  conversationId,
) {
  const response =
    await apiClient.get(
      `/messages/conversations/${conversationId}`,
    );

  return response.data;
}


export async function getMessages(
  conversationId,
) {
  const response =
    await apiClient.get(
      `/messages/conversations/${conversationId}/messages`,
    );

  return response.data;
}


export async function createOrGetConversation(
  userId,
) {
  const response =
    await apiClient.post(
      `/messages/conversations/with/${userId}`,
    );

  return response.data;
}


export async function sendMessage(
  conversationId,
  content,
) {
  const response =
    await apiClient.post(
      `/messages/conversations/${conversationId}/messages`,
      {
        content,
      },
    );

  return response.data;
}


export async function markConversationAsRead(
  conversationId,
) {
  await apiClient.post(
    `/messages/conversations/${conversationId}/read`,
  );
}


export async function updateMessage(
  messageId,
  content,
) {
  const response =
    await apiClient.put(
      `/messages/${messageId}`,
      {
        content,
      },
    );

  return response.data;
}


export async function deleteMessage(
  messageId,
) {
  await apiClient.delete(
    `/messages/${messageId}`,
  );
}
