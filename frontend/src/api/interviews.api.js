import apiClient from "./client";

export async function getMyInterviews() {
  const response =
    await apiClient.get(
      "/interviews/me",
    );

  return response.data;
}

export async function getInterview(
  interviewId,
) {
  const response =
    await apiClient.get(
      `/interviews/${interviewId}`,
    );

  return response.data;
}

export async function getInterviewPreparation(
  interviewId,
) {
  const response =
    await apiClient.get(
      `/interviews/${interviewId}/preparation`,
    );

  return response.data;
}

export async function prepareInterview(
  interviewId,
) {
  const response =
    await apiClient.post(
      `/interviews/${interviewId}/prepare`,
    );

  return response.data;
}
