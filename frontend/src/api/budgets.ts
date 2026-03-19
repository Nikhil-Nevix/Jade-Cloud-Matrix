import api from "./axios";
import { Budget, BudgetAlert } from "@/types";

export const getBudgets = async (): Promise<Budget[]> => {
  const response = await api.get<Budget[]>("/v1/budgets");
  return response.data;
};

export const createBudget = async (data: {
  name: string;
  provider?: string;
  budget_amount: number;
  period: string;
  alert_threshold: number;
}): Promise<Budget> => {
  const response = await api.post<Budget>("/v1/budgets", data);
  return response.data;
};

export const updateBudget = async (id: number, data: Partial<Budget>): Promise<Budget> => {
  const response = await api.put<Budget>(`/v1/budgets/${id}`, data);
  return response.data;
};

export const deleteBudget = async (id: number): Promise<void> => {
  await api.delete(`/v1/budgets/${id}`);
};

export const getBudgetAlerts = async (budgetId: number): Promise<BudgetAlert[]> => {
  const response = await api.get<BudgetAlert[]>(`/v1/budgets/${budgetId}/alerts`);
  return response.data;
};

export const updateBudgetAlert = async (alertId: number, status: string): Promise<BudgetAlert> => {
  const response = await api.put<BudgetAlert>(`/v1/budgets/alerts/${alertId}`, { status });
  return response.data;
};
