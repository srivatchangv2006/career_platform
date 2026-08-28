import apiClient from "./client";

export async function getRecruiterInterviews() {
  const response =
    await apiClient.get(
      "/recruiter/interviews",
    );

  return response.data;
}

export async function createRecruiterInterview(
  payload,
) {
  const response =
    await apiClient.post(
      "/recruiter/interviews",
      payload,
    );

  return response.data;
}

export async function updateRecruiterInterview(
  interviewId,
  payload,
) {
  const response =
    await apiClient.put(
      `/recruiter/interviews/${interviewId}`,
      payload,
    );

  return response.data;
}

export async function deleteRecruiterInterview(
  interviewId,
) {
  await apiClient.delete(
    `/recruiter/interviews/${interviewId}`,
  );
}
