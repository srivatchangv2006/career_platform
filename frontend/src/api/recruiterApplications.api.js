import apiClient from "./client";

export async function getRecruiterApplicants({
  jobId = "",
  status = "",
  search = "",
} = {}) {
  const params = {};

  if (jobId) {
    params.job_id = jobId;
  }

  if (status) {
    params.status_filter = status;
  }

  if (search.trim()) {
    params.search = search.trim();
  }

  const response =
    await apiClient.get(
      "/recruiter/applications/applicants",
      { params },
    );

  return response.data;
}

export async function getRecruiterApplicationDetails(
  applicationId,
) {
  const response =
    await apiClient.get(
      `/recruiter/applications/${applicationId}/details`,
    );

  return response.data;
}

export async function updateRecruiterApplicationStatus(
  applicationId,
  payload,
) {
  const response =
    await apiClient.put(
      `/recruiter/applications/${applicationId}/status`,
      payload,
    );

  return response.data;
}

export async function getRecruiterApplicationAnswers(
  applicationId,
) {
  const response =
    await apiClient.get(
      `/recruiter/applications/${applicationId}/answers`,
    );

  return response.data;
}

export async function downloadRecruiterResume(
  applicationId,
) {
  const response =
    await apiClient.get(
      `/recruiter/applications/${applicationId}/resume`,
      {
        responseType: "blob",
      },
    );

  return {
    blob: response.data,
    contentDisposition:
      response.headers[
        "content-disposition"
      ] || "",
  };
}
