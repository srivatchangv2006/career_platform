import axios from "axios";

const apiClient = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(
      "medai_access_token",
    );

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    /*
     * JSON is Axios' normal behavior for plain
     * JavaScript objects.
     *
     * For FormData, do NOT set Content-Type manually.
     * The browser/Axios will automatically set:
     *
     * multipart/form-data; boundary=...
     */
    if (
      config.data instanceof FormData
    ) {
      delete config.headers[
        "Content-Type"
      ];
      delete config.headers[
        "content-type"
      ];
    }

    return config;
  },
  (error) =>
    Promise.reject(error),
);

export default apiClient;
