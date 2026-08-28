import apiClient from "./client";

export async function getMyResumes() {
  const response = await apiClient.get(
    "/resumes/me",
  );

  return response.data;
}

export async function uploadResume(
  file,
  resumeName,
) {
  const formData = new FormData();

  formData.append("file", file);

  if (resumeName?.trim()) {
    formData.append(
      "resume_name",
      resumeName.trim(),
    );
  }

  const response = await apiClient.post(
    "/resumes/upload",
    formData,
  );

  return response.data;
}

export async function setPrimaryResume(
  resumeId,
) {
  const response = await apiClient.post(
    `/resumes/${resumeId}/primary`,
  );

  return response.data;
}

export async function renameResume(
  resumeId,
  name,
) {
  const response = await apiClient.put(
    `/resumes/${resumeId}/name`,
    {
      name,
    },
  );

  return response.data;
}

export async function deleteResume(
  resumeId,
) {
  await apiClient.delete(
    `/resumes/${resumeId}`,
  );
}
