import api from "./axios";
import { NetworkPricing } from "@/types";

export const getNetworkPricing = async (params?: {
  provider_id?: number;
  source_region_id?: number;
  destination_type?: string;
}): Promise<NetworkPricing[]> => {
  const response = await api.get<NetworkPricing[]>("/v1/network/pricing", { params });
  return response.data;
};

export const calculateNetwork = async (data: {
  transfers: { network_pricing_id: number; transfer_gb: number }[];
  duration_months: number;
}): Promise<any> => {
  const response = await api.post("/v1/network/calculate", data);
  return response.data;
};
