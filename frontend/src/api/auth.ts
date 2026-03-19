import api from "./axios";
import { AuthResponse } from "@/types";

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/v1/auth/login", { email, password });
  return response.data;
};

export const register = async (email: string, password: string, role: string = "user"): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/v1/auth/register", { email, password, role });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get("/v1/auth/me");
  return response.data;
};
