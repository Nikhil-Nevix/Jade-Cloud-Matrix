import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { getCalculations } from "@/api/calculations";
import { getBudgets } from "@/api/budgets";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calculator, History, Wallet, TrendingUp, AlertCircle, DollarSign } from "lucide-react";
import { format } from "date-fns";

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: calculationsData } = useQuery({
    queryKey: ["calculations", { page: 1, limit: 5 }],
    queryFn: () => getCalculations({ page: 1, limit: 5 }),
  });

  const { data: budgets } = useQuery({
    queryKey: ["budgets"],
    queryFn: getBudgets,
  });

  const calculations = calculationsData?.calculations || [];
  const totalCalculations = calculationsData?.total || 0;

  // Compute stats
  const lastCalc = calculations[0];
  const cheapestProviderCounts: Record<string, number> = {};
  calculations.forEach((c) => {
    if (c.cheapest_provider) {
      cheapestProviderCounts[c.cheapest_provider] = (cheapestProviderCounts[c.cheapest_provider] || 0) + 1;
    }
  });
  const mostFrequentProvider = Object.keys(cheapestProviderCounts).sort(
    (a, b) => cheapestProviderCounts[b] - cheapestProviderCounts[a]
  )[0] || "N/A";

  const activeBudgets = budgets?.filter((b) => b.is_active).length || 0;
  const budgetAlerts = budgets?.filter((b) => b.status === "warning" || b.status === "exceeded").length || 0;

  const estimatedSpend = calculations.reduce((sum, c) => {
    const monthly = (c.aws_total_monthly || 0) + (c.azure_total_monthly || 0) + (c.gcp_total_monthly || 0);
    return sum + monthly;
  }, 0);

  const stats = [
    { label: "My Calculations", value: totalCalculations, icon: Calculator, color: "bg-blue-500" },
    { label: "Last Calculation", value: lastCalc ? format(new Date(lastCalc.created_at), "MMM dd") : "N/A", icon: History, color: "bg-purple-500" },
    { label: "Cheapest Provider", value: mostFrequentProvider, icon: TrendingUp, color: "bg-green-500" },
    { label: "Active Budgets", value: activeBudgets, icon: Wallet, color: "bg-indigo-500" },
    { label: "Budget Alerts", value: budgetAlerts, icon: AlertCircle, color: budgetAlerts > 0 ? "bg-red-500" : "bg-gray-400" },
    { label: "Est. Monthly Spend", value: `$${estimatedSpend.toFixed(0)}`, icon: DollarSign, color: "bg-teal-500" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user?.email}</h1>
        <p className="text-gray-600 mt-1">{format(new Date(), "EEEE, MMMM dd, yyyy")}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Calculations */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Calculations</CardTitle>
        </CardHeader>
        <CardContent>
          {calculations.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No calculations yet. Start by creating one!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cheapest</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total/mo</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {calculations.map((calc) => {
                    const totalMonthly = (calc.aws_total_monthly || 0) + (calc.azure_total_monthly || 0) + (calc.gcp_total_monthly || 0);
                    return (
                      <tr key={calc.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">{format(new Date(calc.created_at), "MMM dd, yyyy")}</td>
                        <td className="px-4 py-3 text-sm capitalize">{calc.calc_type}</td>
                        <td className="px-4 py-3 text-sm">{calc.duration_months} months</td>
                        <td className="px-4 py-3 text-sm">{calc.cheapest_provider || "N/A"}</td>
                        <td className="px-4 py-3 text-sm font-semibold">${totalMonthly.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm">
                          <Link to={`/history?view=${calc.id}`}>
                            <Button variant="outline" size="sm">View</Button>
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Budget Status */}
      {budgets && budgets.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Budget Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {budgets.slice(0, 3).map((budget) => (
                <div key={budget.id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium">{budget.name}</p>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className={`h-full rounded-full ${
                          budget.status === "exceeded" ? "bg-red-500" :
                          budget.status === "warning" ? "bg-yellow-500" : "bg-green-500"
                        }`}
                        style={{ width: `${Math.min(budget.pct_used, 100)}%` }}
                      />
                    </div>
                  </div>
                  <span className="ml-4 text-sm font-semibold">{budget.pct_used.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="flex gap-4">
        <Link to="/calculator">
          <Button>
            <Calculator className="w-4 h-4 mr-2" />
            New Calculation
          </Button>
        </Link>
        <Link to="/budgets">
          <Button variant="outline">
            <Wallet className="w-4 h-4 mr-2" />
            View Budgets
          </Button>
        </Link>
        <Link to="/recommendations">
          <Button variant="outline">
            <TrendingUp className="w-4 h-4 mr-2" />
            Get AI Recommendations
          </Button>
        </Link>
      </div>
    </div>
  );
}
