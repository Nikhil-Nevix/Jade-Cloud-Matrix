import api from "./axios";
import { KubernetesPricing } from "@/types";

export const getKubernetesPricing = async (params?: {
  provider_id?: number;
  region_id?: number;
}): Promise<KubernetesPricing[]> => {
  const response = await api.get<KubernetesPricing[]>("/v1/kubernetes/pricing", { params });
  return response.data;
};

export const calculateKubernetes = async (data: {
  provider_id: number;
  region_id: number;
  node_count: number;
  node_type_id: number;
  duration_months: number;
  include_cluster_fee: boolean;
}): Promise<any> => {
  const response = await api.post("/v1/kubernetes/calculate", data);
  return response.data;
};
