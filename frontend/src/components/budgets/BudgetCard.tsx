import React from "react";
import { Budget } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Trash2 } from "lucide-react";

interface BudgetCardProps {
  budget: Budget;
  onEdit: (budget: Budget) => void;
  onDelete: (budget: Budget) => void;
}

export default function BudgetCard({ budget, onEdit, onDelete }: BudgetCardProps) {
  const statusColors = {
    ok: "bg-green-500",
    warning: "bg-yellow-500",
    exceeded: "bg-red-500",
  };

  const statusBadges = {
    ok: "success",
    warning: "warning",
    exceeded: "destructive",
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg">{budget.name}</CardTitle>
            {budget.provider && (
              <p className="text-sm text-gray-600 mt-1">Provider: {budget.provider}</p>
            )}
          </div>
          <Badge variant={statusBadges[budget.status as keyof typeof statusBadges] as any}>
            {budget.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Current Spend</span>
              <span className="font-semibold">
                ${budget.current_spend.toFixed(2)} / ${budget.budget_amount.toFixed(2)}
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className={cn("h-full transition-all", statusColors[budget.status as keyof typeof statusColors])}
                style={{ width: `${Math.min(budget.pct_used, 100)}%` }}
              />
            </div>
            
            <p className="text-xs text-gray-500 mt-1">
              {budget.pct_used.toFixed(1)}% used
            </p>
          </div>

          <div className="text-sm text-gray-600">
            <p>Period: <span className="font-medium capitalize">{budget.period}</span></p>
            <p>Alert Threshold: <span className="font-medium">{budget.alert_threshold}%</span></p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => onEdit(budget)}>
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
            <Button variant="destructive" size="sm" onClick={() => onDelete(budget)}>
              <Trash2 className="w-4 h-4 mr-1" />
              Delete
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
