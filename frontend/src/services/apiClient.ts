import axios from "axios";

// In dev, Vite proxies /api -> http://localhost:8000 (see vite.config.ts),
// so this stays relative and works identically in dev and prod builds
// (prod would set VITE_API_BASE_URL to the deployed API's real origin).
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
  timeout: 10_000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Centralized place to normalize error shape from our FastAPI error
    // middleware ({ error: { code, message, status } }) — components can
    // just read err.message without knowing the backend's exact contract.
    const backendMessage = error?.response?.data?.error?.message;
    if (backendMessage) {
      error.message = backendMessage;
    }
    return Promise.reject(error);
  }
);
