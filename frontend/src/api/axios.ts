import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — add JWT token
api.interceptors.request.use((config) => {
  const stored = localStorage.getItem("jade_auth");
  if (stored) {
    try {
      const auth = JSON.parse(stored);
      if (auth?.token) {
        config.headers.Authorization = `Bearer ${auth.token}`;
      }
    } catch (e) {
      console.error("Failed to parse auth from localStorage", e);
    }
  }
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("jade_auth");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
