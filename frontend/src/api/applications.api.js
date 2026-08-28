import apiClient from "./client";

export async function getMyApplications() {
  const response = await apiClient.get(
    "/applications/me",
  );

  return response.data;
}

export async function createApplication(
  payload,
) {
  const response = await apiClient.post(
    "/applications",
    payload,
  );

  return response.data;
}

export async function getApplicationWorkspace(
  applicationId,
) {
  const response = await apiClient.get(
    `/applications/${applicationId}/workspace`,
  );

  return response.data;
}

export async function getApplicationTimeline(
  applicationId,
) {
  const response = await apiClient.get(
    `/applications/${applicationId}/timeline`,
  );

  return response.data;
}

export async function analyzeSkillGap(
  jobId,
) {
  const response = await apiClient.post(
    `/jobs/${jobId}/skill-gap`,
  );

  return response.data;
}
