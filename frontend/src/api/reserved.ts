import api from "./axios";
import { ReservedPricing } from "@/types";

export const getReservedPricing = async (params?: {
  provider_id?: number;
  region_id?: number;
  instance_type?: string;
  term?: string;
  payment_type?: string;
}): Promise<ReservedPricing[]> => {
  const response = await api.get<ReservedPricing[]>("/v1/reserved/pricing", { params });
  return response.data;
};

export const calculateReserved = async (data: {
  selections: { reserved_pricing_id: number; quantity: number }[];
  duration_months: number;
}): Promise<any> => {
  const response = await api.post("/v1/reserved/calculate", data);
  return response.data;
};
