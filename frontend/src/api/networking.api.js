import apiClient from "./client";

export async function getMyFollowing(query = "") {
  const response = await apiClient.get(
    "/user-follows/me",
    {
      params: query
        ? { q: query }
        : {},
    },
  );

  return response.data;
}

export async function followUser(userId) {
  const response = await apiClient.post(
    `/user-follows/${userId}`,
  );

  return response.data;
}

export async function unfollowUser(userId) {
  await apiClient.delete(
    `/user-follows/${userId}`,
  );
}

export async function getFollowers(
  userId,
  query = "",
) {
  const response = await apiClient.get(
    `/user-follows/${userId}`,
    {
      params: query
        ? { q: query }
        : {},
    },
  );

  return response.data;
}

export async function getMyConnections(
  query = "",
) {
  const response = await apiClient.get(
    "/connections/me",
    {
      params: query
        ? { q: query }
        : {},
    },
  );

  return response.data;
}

export async function getConnectionRequests(
  query = "",
) {
  const response = await apiClient.get(
    "/connections/requests",
    {
      params: query
        ? { q: query }
        : {},
    },
  );

  return response.data;
}

export async function createConnection(
  receiverId,
) {
  const response = await apiClient.post(
    "/connections",
    {
      receiver_id: receiverId,
    },
  );

  return response.data;
}

export async function updateConnection(
  connectionId,
  status,
) {
  const response = await apiClient.put(
    `/connections/${connectionId}`,
    {
      status,
    },
  );

  return response.data;
}

export async function deleteConnection(
  connectionId,
) {
  await apiClient.delete(
    `/connections/${connectionId}`,
  );
}
