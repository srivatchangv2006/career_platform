import apiClient from "./client";


export async function getReferralJobs() {
  const response =
    await apiClient.get(
      "/jobs",
    );

  const data = response.data;

  if (Array.isArray(data)) {
    return data.filter(
      (job) =>
        job &&
        job.id &&
        job.title &&
        job.status === "OPEN",
    );
  }

  if (
    data &&
    Array.isArray(data.items)
  ) {
    return data.items.filter(
      (job) =>
        job &&
        job.id &&
        job.title &&
        job.status === "OPEN",
    );
  }

  if (
    data &&
    Array.isArray(data.jobs)
  ) {
    return data.jobs.filter(
      (job) =>
        job &&
        job.id &&
        job.title &&
        job.status === "OPEN",
    );
  }

  return [];
}


export async function getReferralOpportunities() {
  const response =
    await apiClient.get(
      "/referral-opportunities",
    );

  return response.data;
}


export async function createReferralOpportunity(
  payload,
) {
  const response =
    await apiClient.post(
      "/referral-opportunities",
      payload,
    );

  return response.data;
}


export async function updateReferralOpportunity(
  opportunityId,
  payload,
) {
  const response =
    await apiClient.put(
      `/referral-opportunities/${opportunityId}`,
      payload,
    );

  return response.data;
}


export async function deleteReferralOpportunity(
  opportunityId,
) {
  await apiClient.delete(
    `/referral-opportunities/${opportunityId}`,
  );
}


export async function getSentReferralRequests() {
  const response =
    await apiClient.get(
      "/referral-requests/sent",
    );

  return response.data;
}


export async function getReceivedReferralRequests() {
  const response =
    await apiClient.get(
      "/referral-requests/received",
    );

  return response.data;
}


export async function createReferralRequest(
  opportunityId,
  payload,
) {
  const response =
    await apiClient.post(
      `/referral-requests/for/${opportunityId}`,
      payload,
    );

  return response.data;
}


export async function updateReferralRequest(
  referralId,
  payload,
) {
  const response =
    await apiClient.put(
      `/referral-requests/${referralId}`,
      payload,
    );

  return response.data;
}


export async function getReferralResumeBlob(
  referralId,
) {
  const response =
    await apiClient.get(
      `/referral-requests/${referralId}/resume`,
      {
        responseType: "blob",
      },
    );

  return response.data;
}
