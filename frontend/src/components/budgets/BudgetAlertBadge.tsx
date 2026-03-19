import React from "react";
import { Badge } from "@/components/ui/badge";

interface BudgetAlertBadgeProps {
  status: string;
}

export default function BudgetAlertBadge({ status }: BudgetAlertBadgeProps) {
  const variants = {
    active: "destructive",
    acknowledged: "warning",
    resolved: "success",
  };

  return (
    <Badge variant={variants[status as keyof typeof variants] as any}>
      {status}
    </Badge>
  );
}
