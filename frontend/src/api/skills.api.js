import apiClient from "./client";

export async function getSkills() {
  const response = await apiClient.get(
    "/skills",
  );

  return response.data;
}

export async function getJobSkills(
  jobId,
) {
  const response = await apiClient.get(
    `/jobs/${jobId}/skills`,
  );

  return response.data;
}

export async function addJobSkill(
  jobId,
  payload,
) {
  const response = await apiClient.post(
    `/jobs/${jobId}/skills`,
    payload,
  );

  return response.data;
}

export async function deleteJobSkill(
  jobId,
  skillId,
) {
  await apiClient.delete(
    `/jobs/${jobId}/skills/${skillId}`,
  );
}
