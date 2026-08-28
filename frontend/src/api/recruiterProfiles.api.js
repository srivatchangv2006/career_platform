import apiClient from "./client";

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

export async function updateMyRecruiterProfile(
  payload,
) {
  const response = await apiClient.put(
    "/recruiter-profiles/me",
    payload,
  );

  return response.data;
}
