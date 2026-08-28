import apiClient from "./client";

export async function loginUser(credentials) {
  const response = await apiClient.post(
    "/users/login",
    credentials,
  );

  return response.data;
}

export async function registerUser(payload) {
  const response = await apiClient.post(
    "/users/register",
    payload,
  );

  return response.data;
}

export async function getCurrentUser() {
  const response = await apiClient.get("/users/me");

  return response.data;
}
