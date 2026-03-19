import api from "./axios";
import { ComputePricing, StoragePricing } from "@/types";

export const getComputePricing = async (params?: {
  provider_id?: number;
  region_id?: number;
  os_type?: string;
}): Promise<ComputePricing[]> => {
  const response = await api.get<ComputePricing[]>("/v1/pricing/compute", { params });
  return response.data;
};

export const getStoragePricing = async (params?: {
  provider_id?: number;
  region_id?: number;
  storage_type?: string;
}): Promise<StoragePricing[]> => {
  const response = await api.get<StoragePricing[]>("/v1/pricing/storage", { params });
  return response.data;
};
