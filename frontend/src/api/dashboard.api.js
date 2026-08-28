import apiClient from "./client";

export async function getRecruiterDashboard() {
  const response = await apiClient.get(
    "/recruiter/dashboard",
  );

  return response.data;
}

export async function getRecruiterApplicants(
  params = {},
) {
  const response = await apiClient.get(
    "/recruiter/applicants",
    {
      params,
    },
  );

  return response.data;
}

export async function getMyApplications() {
  const response = await apiClient.get(
    "/applications",
  );

  return response.data;
}

export async function getJobs() {
  const response = await apiClient.get(
    "/jobs",
  );

  return response.data;
}

export async function generateJobRecommendations() {
  const response = await apiClient.post(
    "/recommendations/jobs",
  );

  return response.data;
}

export async function getRecommendationItems(
  runId,
) {
  const response = await apiClient.get(
    `/recommendations/jobs/${runId}/items`,
  );

  return response.data;
}
