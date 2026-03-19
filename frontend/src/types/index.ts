export interface AuthResponse {
  user_id: number;
  email: string;
  role: string;
  token: string;
  expires_at: string;
}

export interface User {
  id: number;
  email: string;
  role: string;
  created_at: string;
  last_login?: string;
}

export interface Provider {
  id: number;
  name: string;
  created_at: string;
}

export interface Region {
  id: number;
  provider_id: number;
  region_code: string;
  region_name: string;
  created_at: string;
}

export interface ComputePricing {
  id: number;
  region_id: number;
  provider_id: number;
  provider_name?: string;
  region_code?: string;
  region_name?: string;
  instance_type: string;
  os_type: string;
  price_per_hour: number;
  price_per_month: number;
  price_per_year: number;
  vcpu: number;
  memory_gb: number;
  updated_at: string;
}

export interface StoragePricing {
  id: number;
  region_id: number;
  provider_id: number;
  provider_name?: string;
  region_code?: string;
  region_name?: string;
  storage_type: string;
  storage_name: string;
  price_per_gb: number;
  price_per_gb_month: number;
  unit_type: string;
  updated_at: string;
}

export interface ReservedPricing {
  id: number;
  region_id: number;
  provider_id: number;
  provider_name?: string;
  region_code?: string;
  region_name?: string;
  instance_type: string;
  os_type: string;
  term: string;
  payment_type: string;
  upfront_cost: number;
  monthly_cost: number;
  effective_hourly: number;
  savings_vs_ondemand: number;
  updated_at: string;
}

export interface KubernetesPricing {
  id: number;
  region_id: number;
  provider_id: number;
  provider_name?: string;
  region_code?: string;
  region_name?: string;
  node_type: string;
  vcpu: number;
  memory_gb: number;
  price_per_hour: number;
  price_per_month: number;
  cluster_fee_monthly: number;
  updated_at: string;
}

export interface NetworkPricing {
  id: number;
  provider_id: number;
  provider_name?: string;
  source_region_id: number;
  region_code?: string;
  destination_type: string;
  price_per_gb: number;
  free_tier_gb: number;
  updated_at: string;
}

export interface ProviderBreakdown {
  provider_name: string;
  compute_cost_monthly: number;
  storage_cost_monthly: number;
  total_cost_monthly: number;
  total_cost_annual: number;
  is_cheapest: boolean;
}

export interface Calculation {
  id: number;
  user_id: number;
  calc_type: string;
  input_json: any;
  result_json: any;
  cheapest_provider?: string;
  aws_total_monthly?: number;
  azure_total_monthly?: number;
  gcp_total_monthly?: number;
  aws_total_annual?: number;
  azure_total_annual?: number;
  gcp_total_annual?: number;
  duration_months: number;
  created_at: string;
  provider_breakdowns?: ProviderBreakdown[];
}

export interface Budget {
  id: number;
  user_id: number;
  name: string;
  provider?: string;
  budget_amount: number;
  period: string;
  alert_threshold: number;
  is_active: boolean;
  current_spend: number;
  pct_used: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetAlert {
  id: number;
  budget_id: number;
  triggered_at: string;
  current_spend: number;
  threshold_pct: number;
  status: string;
  message?: string;
}

export interface Recommendation {
  title: string;
  category: string;
  priority: string;
  estimated_monthly_savings: number;
  estimated_annual_savings: number;
  description: string;
  action_steps: string[];
  affected_providers: string[];
}

export interface RecommendationResponse {
  id: string;
  generated_at: string;
  calculations_analysed: number;
  recommendations: Recommendation[];
  total_estimated_monthly_savings: number;
  total_estimated_annual_savings: number;
  summary: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  input_data?: any;
  status: string;
  error_message?: string;
  ip_address?: string;
  timestamp: string;
}

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
