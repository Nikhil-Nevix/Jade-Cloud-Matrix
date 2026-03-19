import api from "./axios";
import { Calculation, ComputeSelection, StorageSelection } from "@/types";

export interface CalculateRequest {
  compute_selections: ComputeSelection[];
  storage_selections: StorageSelection[];
  duration_months: number;
}

export const calculatePricing = async (request: CalculateRequest): Promise<Calculation> => {
  const response = await api.post<Calculation>("/v1/calculations", request);
  return response.data;
};

export const getCalculations = async (params?: {
  page?: number;
  limit?: number;
  from_date?: string;
  to_date?: string;
  calc_type?: string;
  min_cost?: number;
  max_cost?: number;
  provider?: string;
  cheapest_provider?: string;
}): Promise<{ calculations: Calculation[]; total: number; page: number; limit: number }> => {
  const response = await api.get("/v1/calculations", { params });
  return response.data;
};

export const getCalculation = async (id: number): Promise<Calculation> => {
  const response = await api.get<Calculation>(`/v1/calculations/${id}`);
  return response.data;
};

export const deleteCalculation = async (id: number): Promise<void> => {
  await api.delete(`/v1/calculations/${id}`);
};
