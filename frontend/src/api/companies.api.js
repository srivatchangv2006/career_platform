import apiClient from "./client";

export async function getCompanies() {
  const response = await apiClient.get(
    "/companies",
  );

  return response.data;
}
