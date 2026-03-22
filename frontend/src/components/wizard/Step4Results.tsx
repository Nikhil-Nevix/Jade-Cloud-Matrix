import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, RotateCcw, ChevronDown, ChevronUp } from "lucide-react";
import { MultiCloudCompareResult } from "@/api/wizard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface Step4Props {
  results: MultiCloudCompareResult;
  onStartOver: () => void;
  onExportPDF: () => void;
  onExportExcel: () => void;
}

export default function Step4Results({ results, onStartOver, onExportPDF, onExportExcel }: Step4Props) {
  const [showMappings, setShowMappings] = useState(false);

  // Prepare chart data
  const chartData = results.provider_breakdowns.map((breakdown) => ({
    provider: breakdown.provider_name,
    compute: breakdown.compute_cost_monthly,
    storage: breakdown.storage_cost_monthly,
    total: breakdown.total_cost_monthly,
  }));

  const cheapestBreakdown = results.provider_breakdowns.find((b) => b.is_cheapest);

  return (
    <div className="space-y-6">
      {/* Header with Export Buttons */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Step 4: Analysis Complete</h2>
          <p className="text-gray-600 mt-1">
            Optimal provider identified for {results.duration_months} month commitment
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onExportPDF}>
            <FileText className="w-4 h-4 mr-2" />
            PDF Report
          </Button>
          <Button variant="outline" onClick={onExportExcel}>
            <Download className="w-4 h-4 mr-2" />
            Excel Data
          </Button>
        </div>
      </div>

      {/* Winner Badge */}
      {cheapestBreakdown && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400 rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <Badge className="bg-green-600 text-white text-lg px-4 py-2 mb-2">
                🏆 CHEAPEST
              </Badge>
              <h3 className="text-3xl font-bold text-gray-900">{cheapestBreakdown.provider_name}</h3>
              <p className="text-lg text-gray-700 mt-2">
                ${cheapestBreakdown.total_cost_monthly.toFixed(2)}/month • $
                {cheapestBreakdown.total_cost_annual.toFixed(2)}/year
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Cost Comparison Chart */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Comparison Breakdown</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData} barSize={60}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="provider" stroke="#6b7280" fontSize={14} fontWeight={600} />
            <YAxis
              stroke="#6b7280"
              fontSize={12}
              label={{ value: "Cost ($/month)", angle: -90, position: "insideLeft", style: { fill: "#6b7280" } }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
              formatter={(value: number) => `$${value.toFixed(2)}`}
            />
            <Legend wrapperStyle={{ paddingTop: "20px" }} />
            <Bar dataKey="compute" fill="#3B82F6" name="Compute ($/mo)" radius={[8, 8, 0, 0]} />
            <Bar dataKey="storage" fill="#10B981" name="Storage ($/mo)" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Cost Comparison Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Provider</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Monthly Total</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Compute</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Storage</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Annual Est.</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {results.provider_breakdowns.map((breakdown, index) => (
                <tr
                  key={breakdown.provider_name}
                  className={breakdown.is_cheapest ? "bg-green-50 border-l-4 border-green-500" : ""}
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {breakdown.provider_name}
                    {breakdown.is_cheapest && (
                      <Badge className="ml-2 bg-green-600 text-white">Cheapest</Badge>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                    ${breakdown.total_cost_monthly.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-right text-gray-700">
                    ${breakdown.compute_cost_monthly.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-right text-gray-700">
                    ${breakdown.storage_cost_monthly.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-right font-medium text-gray-900">
                    ${breakdown.total_cost_annual.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Instance Equivalence Mapping */}
      {results.instance_mappings && results.instance_mappings.length > 0 && (
        <div className="bg-white rounded-lg border">
          <button
            onClick={() => setShowMappings(!showMappings)}
            className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Auto-Mapped Equivalent Instances</h3>
              <p className="text-sm text-gray-600 mt-1">
                See how your baseline instances were mapped across providers
              </p>
            </div>
            {showMappings ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {showMappings && (
            <div className="px-6 pb-6">
              <div className="overflow-x-auto">
                <table className="w-full mt-4">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Your Selection</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Specs</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Qty</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-blue-600">AWS</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-blue-600">Azure</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-blue-600">GCP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {results.instance_mappings.map((mapping, index) => (
                      <tr key={index}>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {mapping.base_instance}
                          <div className="text-xs text-gray-500">{mapping.base_provider}</div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          {mapping.vcpu} vCPU
                          <br />
                          {mapping.memory_gb} GB RAM
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">×{mapping.quantity}</td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          {mapping.equivalents.AWS ? (
                            <div>
                              <div className="font-medium">{mapping.equivalents.AWS.instance_type}</div>
                              <div className="text-xs text-gray-500">
                                ${mapping.equivalents.AWS.price_per_month.toFixed(2)}/mo
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400 italic">Not available</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          {mapping.equivalents.Azure ? (
                            <div>
                              <div className="font-medium">{mapping.equivalents.Azure.instance_type}</div>
                              <div className="text-xs text-gray-500">
                                ${mapping.equivalents.Azure.price_per_month.toFixed(2)}/mo
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400 italic">Not available</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          {mapping.equivalents.GCP ? (
                            <div>
                              <div className="font-medium">{mapping.equivalents.GCP.instance_type}</div>
                              <div className="text-xs text-gray-500">
                                ${mapping.equivalents.GCP.price_per_month.toFixed(2)}/mo
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400 italic">Not available</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Start Over Button */}
      <div className="flex justify-center pt-4">
        <Button variant="outline" onClick={onStartOver} size="lg">
          <RotateCcw className="w-4 h-4 mr-2" />
          Start Over
        </Button>
      </div>
    </div>
  );
}
