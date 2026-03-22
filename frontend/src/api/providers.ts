import api from "./axios";
import { Provider, Region } from "@/types";

export const getProviders = async (): Promise<Provider[]> => {
  const response = await api.get<Provider[]>("/v1/providers");
  return response.data;
};

export const getProviderRegions = async (providerId: number): Promise<Region[]> => {
  const response = await api.get<Region[]>(`/v1/providers/${providerId}/regions`);
  return response.data;
};

// Alias for compatibility
export const getRegions = getProviderRegions;
