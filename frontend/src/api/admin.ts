import api from "./axios";
import { User, AuditLog } from "@/types";

export const getAllUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>("/v1/admin/users");
  return response.data;
};

export const createUser = async (data: {
  email: string;
  password: string;
  role: string;
}): Promise<User> => {
  const response = await api.post<User>("/v1/admin/users", data);
  return response.data;
};

export const updateUser = async (id: number, data: Partial<User> & { password?: string }): Promise<User> => {
  const response = await api.put<User>(`/v1/admin/users/${id}`, data);
  return response.data;
};

export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/v1/admin/users/${id}`);
};

export const getAuditLogs = async (params?: {
  page?: number;
  limit?: number;
  user_id?: number;
  action?: string;
  from_date?: string;
  to_date?: string;
}): Promise<{ logs: AuditLog[]; total: number; page: number; limit: number }> => {
  const response = await api.get("/v1/admin/audit-logs", { params });
  return response.data;
};

export const getAdminStats = async (): Promise<any> => {
  const response = await api.get("/v1/admin/stats");
  return response.data;
};

export const triggerIngestion = async (): Promise<{ message: string }> => {
  const response = await api.post("/v1/admin/ingest");
  return response.data;
};

// Aliases for compatibility
export const getAdminUsers = getAllUsers;
export const createAdminUser = createUser;
export const updateAdminUser = updateUser;
export const deleteAdminUser = deleteUser;
export const getAdminAuditLogs = getAuditLogs;
