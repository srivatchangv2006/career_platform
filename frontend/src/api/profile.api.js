import apiClient from "./client";

export async function getMyCandidateProfile() {
  const response = await apiClient.get(
    "/profiles/me",
  );

  return response.data;
}

export async function createCandidateProfile(
  payload,
) {
  const response = await apiClient.post(
    "/profiles",
    payload,
  );

  return response.data;
}

export async function updateCandidateProfile(
  payload,
) {
  const response = await apiClient.put(
    "/profiles/me",
    payload,
  );

  return response.data;
}

export async function getMyRecruiterProfile() {
  const response = await apiClient.get(
    "/recruiter-profiles/me",
  );

  return response.data;
}

export async function createRecruiterProfile(
  payload,
) {
  const response = await apiClient.post(
    "/recruiter-profiles/me",
    payload,
  );

  return response.data;
}

export async function updateRecruiterProfile(
  payload,
) {
  const response = await apiClient.put(
    "/recruiter-profiles/me",
    payload,
  );

  return response.data;
}

export async function getPublicProfile(userId) {
  const response = await apiClient.get(
    `/profiles/${userId}`,
  );

  return response.data;
}
