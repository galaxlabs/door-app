import axios from "axios";

function resolveApiBaseUrl() {
  const env = process.env.NEXT_PUBLIC_API_URL;
  if (!env) return "/api/v1";

  if (typeof window === "undefined") return env;

  const host = window.location.hostname;
  const isBrowserOnLocalhost = host === "localhost" || host === "127.0.0.1";
  const envIsLoopback = env.startsWith("http://localhost") || env.startsWith("http://127.0.0.1");

  if (!isBrowserOnLocalhost && envIsLoopback) {
    return "/api/v1";
  }

  return env;
}

const API_BASE_URL = resolveApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const refreshPath = "/auth/token/refresh/";
          const refreshUrl =
            typeof API_BASE_URL === "string" && API_BASE_URL.startsWith("http")
              ? `${API_BASE_URL}${refreshPath}`
              : `${window.location.origin}${API_BASE_URL}${refreshPath}`;
          const { data } = await axios.post(refreshUrl, { refresh });
          localStorage.setItem("access_token", data.access);
          error.config.headers.Authorization = `Bearer ${data.access}`;
          return api(error.config);
        } catch {
          localStorage.clear();
          window.location.href = "/auth/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
