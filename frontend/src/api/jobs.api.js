import apiClient from "./client";

export async function getJobs() {
  const response = await apiClient.get(
    "/jobs",
  );

  return response.data;
}

export async function getMyJobs() {
  const response = await apiClient.get(
    "/jobs/mine",
  );

  return response.data;
}

export async function getJob(jobId) {
  const response = await apiClient.get(
    `/jobs/${jobId}`,
  );

  return response.data;
}

export async function createJob(
  payload,
) {
  const response = await apiClient.post(
    "/jobs",
    payload,
  );

  return response.data;
}

export async function updateJob(
  jobId,
  payload,
) {
  const response = await apiClient.put(
    `/jobs/${jobId}`,
    payload,
  );

  return response.data;
}
