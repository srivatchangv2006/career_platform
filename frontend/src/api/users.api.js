import apiClient from "./client";

export async function searchUsers(query) {
  const response = await apiClient.get(
    "/users/search",
    {
      params: {
        q: query,
      },
    },
  );

  return response.data;
}
