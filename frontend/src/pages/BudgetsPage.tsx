import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getBudgets, createBudget, updateBudget, deleteBudget, getBudgetAlerts, updateBudgetAlert } from "@/api/budgets";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import BudgetCard from "@/components/budgets/BudgetCard";
import BudgetAlertBadge from "@/components/budgets/BudgetAlertBadge";
import { Plus, X } from "lucide-react";
import { format } from "date-fns";
import toast from "react-hot-toast";
import type { Budget, BudgetAlert } from "@/types";

export default function BudgetsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);

  const { data: budgets, refetch } = useQuery({
    queryKey: ["budgets"],
    queryFn: getBudgets,
  });

  const { data: alerts } = useQuery({
    queryKey: ["budget-alerts"],
    queryFn: async () => {
      if (!budgets) return [];
      const allAlerts = await Promise.all(
        budgets.map((b) => getBudgetAlerts(b.id))
      );
      return allAlerts.flat();
    },
    enabled: !!budgets,
  });

  const createMutation = useMutation({
    mutationFn: createBudget,
    onSuccess: () => {
      toast.success("Budget created!");
      setShowCreateForm(false);
      refetch();
    },
    onError: () => toast.error("Failed to create budget"),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteBudget,
    onSuccess: () => {
      toast.success("Budget deleted!");
      refetch();
    },
    onError: () => toast.error("Failed to delete budget"),
  });

  const activeAlerts = alerts?.filter((a) => a.status === "active") || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budget Management</h1>
          <p className="text-gray-600 mt-1">Track spending and set alerts</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Budget
        </Button>
      </div>

      {activeAlerts.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900">Active Budget Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeAlerts.map((alert) => (
                <AlertRow key={alert.id} alert={alert} onUpdate={() => refetch()} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {showCreateForm && (
        <BudgetFormModal
          onClose={() => setShowCreateForm(false)}
          onSave={(data) => createMutation.mutate(data)}
        />
      )}

      {editingBudget && (
        <BudgetFormModal
          budget={editingBudget}
          onClose={() => setEditingBudget(null)}
          onSave={(data) => {
            // TODO: implement update
            toast.info("Edit functionality pending");
            setEditingBudget(null);
          }}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets?.map((budget) => (
          <BudgetCard
            key={budget.id}
            budget={budget}
            onEdit={setEditingBudget}
            onDelete={(b) => deleteMutation.mutate(b.id)}
          />
        ))}
      </div>

      {budgets?.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <p>No budgets yet. Create one to start tracking your spending!</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface AlertRowProps {
  alert: BudgetAlert;
  onUpdate: () => void;
}

function AlertRow({ alert, onUpdate }: AlertRowProps) {
  const mutation = useMutation({
    mutationFn: (status: string) => updateBudgetAlert(alert.id, status),
    onSuccess: () => {
      toast.success("Alert updated");
      onUpdate();
    },
    onError: () => toast.error("Failed to update alert"),
  });

  return (
    <div className="flex items-start justify-between border-b pb-3">
      <div>
        <p className="font-medium text-red-900">{alert.message}</p>
        <p className="text-sm text-red-700 mt-1">
          Triggered {format(new Date(alert.triggered_at), "MMM dd, yyyy 'at' HH:mm")}
        </p>
        <p className="text-sm text-red-700">
          Spend: ${alert.current_spend.toFixed(2)} ({alert.threshold_pct}% of budget)
        </p>
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => mutation.mutate("acknowledged")}
          disabled={mutation.isPending}
        >
          Acknowledge
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => mutation.mutate("resolved")}
          disabled={mutation.isPending}
        >
          Resolve
        </Button>
      </div>
    </div>
  );
}

interface BudgetFormModalProps {
  budget?: Budget;
  onClose: () => void;
  onSave: (data: any) => void;
}

function BudgetFormModal({ budget, onClose, onSave }: BudgetFormModalProps) {
  const [name, setName] = useState(budget?.name || "");
  const [provider, setProvider] = useState(budget?.provider || "");
  const [amount, setAmount] = useState(budget?.budget_amount || 1000);
  const [period, setPeriod] = useState(budget?.period || "monthly");
  const [threshold, setThreshold] = useState(budget?.alert_threshold || 80);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      name,
      provider: provider || undefined,
      budget_amount: amount,
      period,
      alert_threshold: threshold,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-lg m-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{budget ? "Edit Budget" : "Create Budget"}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Budget Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Q1 2025 Infrastructure"
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label>Provider (optional)</Label>
              <Select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="mt-1"
              >
                <option value="">All Providers</option>
                <option value="AWS">AWS</option>
                <option value="Azure">Azure</option>
                <option value="GCP">GCP</option>
              </Select>
            </div>

            <div>
              <Label>Budget Amount ($)</Label>
              <Input
                type="number"
                min="1"
                value={amount}
                onChange={(e) => setAmount(parseFloat(e.target.value) || 1000)}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label>Period</Label>
              <Select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="mt-1"
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annual">Annual</option>
              </Select>
            </div>

            <div>
              <Label>Alert Threshold (%)</Label>
              <Input
                type="number"
                min="1"
                max="100"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value) || 80)}
                required
                className="mt-1"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {budget ? "Update Budget" : "Create Budget"}
              </Button>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
