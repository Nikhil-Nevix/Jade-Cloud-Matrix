import React from "react";
import { CalculationResult } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, FileText } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { downloadPDF, downloadExcel } from "@/lib/export";

interface ResultsPanelProps {
  results: CalculationResult;
}

export default function ResultsPanel({ results }: ResultsPanelProps) {
  // Prepare chart data
  const chartData = [
    { provider: "AWS", monthly: results.aws_total_monthly || 0, annual: results.aws_total_annual || 0 },
    { provider: "Azure", monthly: results.azure_total_monthly || 0, annual: results.azure_total_annual || 0 },
    { provider: "GCP", monthly: results.gcp_total_monthly || 0, annual: results.gcp_total_annual || 0 },
  ].filter((d) => d.monthly > 0);

  const handleExport = (format: "pdf" | "excel") => {
    if (format === "pdf") {
      downloadPDF(results.id);
    } else {
      downloadExcel(results.id);
    }
  };

  return (
    <div className="space-y-6 mt-8">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Cost Comparison Results</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => handleExport("pdf")}>
                <FileText className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport("excel")}>
                <Download className="w-4 h-4 mr-2" />
                Export Excel
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Monthly Comparison Chart */}
            <div>
              <h4 className="font-semibold mb-4">Monthly Cost Comparison</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="provider" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                  <Legend />
                  <Bar dataKey="monthly" fill="#3b82f6" name="Monthly Cost" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Provider Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {chartData.map((data) => {
                const isWinner = results.cheapest_provider === data.provider;
                return (
                  <Card key={data.provider} className={isWinner ? "border-2 border-green-500" : ""}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-semibold text-lg">{data.provider}</h5>
                        {isWinner && <Badge variant="success">Cheapest</Badge>}
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Monthly:</span>
                          <span className="font-semibold">${data.monthly.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Annual:</span>
                          <span className="font-semibold">${data.annual.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duration ({results.duration_months}mo):</span>
                          <span className="font-semibold">${(data.monthly * results.duration_months).toFixed(2)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Recommendation */}
            {results.cheapest_provider && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">💡 Recommendation</h4>
                <p className="text-green-800">
                  Based on your configuration, <span className="font-semibold">{results.cheapest_provider}</span> offers
                  the most cost-effective solution for this workload.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
