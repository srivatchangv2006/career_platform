import apiClient from "./client";

export async function getMyProfile() {
  const response = await apiClient.get(
    "/profiles/me",
  );

  return response.data;
}

export async function getPublicProfile(userId) {
  const response = await apiClient.get(
    `/profiles/${userId}`,
  );

  return response.data;
}

export async function createProfile(payload) {
  const response = await apiClient.post(
    "/profiles",
    payload,
  );

  return response.data;
}

export async function updateMyProfile(payload) {
  const response = await apiClient.put(
    "/profiles/me",
    payload,
  );

  return response.data;
}
