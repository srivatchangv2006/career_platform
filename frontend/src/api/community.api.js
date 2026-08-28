import apiClient from "./client";

export async function getCommunityPosts() {
  const response =
    await apiClient.get(
      "/community/posts",
    );

  return response.data;
}

export async function createCommunityPost(
  formData,
) {
  const response =
    await apiClient.post(
      "/community/posts",
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      },
    );

  return response.data;
}

export async function updateCommunityPost(
  postId,
  payload,
) {
  const response =
    await apiClient.put(
      `/community/posts/${postId}`,
      payload,
    );

  return response.data;
}

export async function deleteCommunityPost(
  postId,
) {
  await apiClient.delete(
    `/community/posts/${postId}`,
  );
}

export async function getCommunityPostImages(
  postId,
) {
  const response =
    await apiClient.get(
      `/community/posts/${postId}/images`,
    );

  return response.data;
}

export function getCommunityImageUrl(
  postId,
  imageId,
) {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";

  return `${baseUrl}/community/posts/${postId}/images/${imageId}`;
}

export async function getCommunityComments(
  postId,
) {
  const response =
    await apiClient.get(
      `/community/posts/${postId}/comments`,
    );

  return response.data;
}

export async function createCommunityComment(
  postId,
  payload,
) {
  const response =
    await apiClient.post(
      `/community/posts/${postId}/comments`,
      payload,
    );

  return response.data;
}

export async function updateCommunityComment(
  commentId,
  payload,
) {
  const response =
    await apiClient.put(
      `/community/comments/${commentId}`,
      payload,
    );

  return response.data;
}

export async function deleteCommunityComment(
  commentId,
) {
  await apiClient.delete(
    `/community/comments/${commentId}`,
  );
}

export async function voteCommunityPost(
  postId,
  vote,
) {
  const response =
    await apiClient.post(
      `/community/posts/${postId}/vote`,
      {
        vote,
      },
    );

  return response.data;
}

export async function removeCommunityPostVote(
  postId,
) {
  await apiClient.delete(
    `/community/posts/${postId}/vote`,
  );
}


export async function getCommunityImageBlob(
  postId,
  imageId,
) {
  const response =
    await apiClient.get(
      `/community/posts/${postId}/images/${imageId}`,
      {
        responseType: "blob",
      },
    );

  return response.data;
}
