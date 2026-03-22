import api from "./axios";

export interface ComputeSelection {
  provider_id: number;
  region_id: number;
  compute_pricing_id: number;
  quantity: number;
}

export interface StorageSelection {
  provider_id: number;
  region_id: number;
  storage_pricing_id: number;
  size_gb: number;
}

export interface MultiCloudCompareRequest {
  compute_selections: ComputeSelection[];
  storage_selections: StorageSelection[];
  duration_months: number;
}

export interface EquivalentInstance {
  instance_type: string;
  vcpu: number;
  memory_gb: number;
  price_per_month: number;
}

export interface InstanceMapping {
  base_instance: string;
  base_provider: string;
  vcpu: number;
  memory_gb: number;
  quantity: number;
  equivalents: {
    [provider: string]: EquivalentInstance | null;
  };
}

export interface ProviderBreakdown {
  provider_name: string;
  compute_cost_monthly: number;
  storage_cost_monthly: number;
  total_cost_monthly: number;
  total_cost_annual: number;
  total_for_duration?: number;
  is_cheapest: boolean;
}

export interface MultiCloudCompareResult {
  id: number;
  provider_breakdowns: ProviderBreakdown[];
  instance_mappings: InstanceMapping[];
  cheapest_provider: string;
  duration_months: number;
  total_instances: number;
  total_storage_volumes: number;
  aws_total_monthly?: number;
  azure_total_monthly?: number;
  gcp_total_monthly?: number;
  created_at: string;
}

export const calculateMultiCloudComparison = async (
  request: MultiCloudCompareRequest
): Promise<MultiCloudCompareResult> => {
  const response = await api.post("/v1/calculations/multicloud-compare", request);
  return response.data;
};
