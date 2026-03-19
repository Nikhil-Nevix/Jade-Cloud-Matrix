import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getAdminStats } from "@/api/admin";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, Calculator, FileText, Database, RefreshCw } from "lucide-react";
import { format } from "date-fns";
import toast from "react-hot-toast";
import axios from "@/api/axios";

export default function AdminDashboardPage() {
  const { data: stats, refetch } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: getAdminStats,
  });

  const handleIngest = async () => {
    try {
      await axios.post("/api/v1/admin/ingest");
      toast.success("Pricing ingestion triggered. Data will be updated shortly.");
      refetch();
    } catch (error) {
      toast.error("Failed to trigger ingestion");
    }
  };

  const statCards = [
    { label: "Total Users", value: stats?.total_users || 0, icon: Users, color: "bg-blue-500" },
    { label: "Total Calculations", value: stats?.total_calculations || 0, icon: Calculator, color: "bg-purple-500" },
    { label: "Active Users (30d)", value: stats?.active_users_last_30_days || 0, icon: Users, color: "bg-green-500" },
    { label: "Total Budgets", value: stats?.total_budgets || 0, icon: Database, color: "bg-indigo-500" },
    { label: "Audit Logs", value: stats?.total_audit_logs || 0, icon: FileText, color: "bg-orange-500" },
    { label: "Pricing Records", value: stats?.pricing_data_count || 0, icon: Database, color: "bg-teal-500" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">Platform administration and monitoring</p>
        </div>
        <Button onClick={handleIngest}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Trigger Pricing Ingestion
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
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

      {stats?.last_ingestion && (
        <Card>
          <CardHeader>
            <CardTitle>Last Pricing Ingestion</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">
              {format(new Date(stats.last_ingestion), "EEEE, MMMM dd, yyyy 'at' HH:mm:ss")}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Next scheduled ingestion: 2:00 AM UTC daily
            </p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Application Version</p>
              <p className="font-semibold">1.0.0</p>
            </div>
            <div>
              <p className="text-gray-600">Environment</p>
              <p className="font-semibold">Development</p>
            </div>
            <div>
              <p className="text-gray-600">Database</p>
              <p className="font-semibold">PostgreSQL 15</p>
            </div>
            <div>
              <p className="text-gray-600">Backend</p>
              <p className="font-semibold">FastAPI (Python 3.11)</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
