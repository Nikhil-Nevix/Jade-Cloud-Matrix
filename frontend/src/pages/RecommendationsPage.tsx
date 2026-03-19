import React, { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getCalculations } from "@/api/calculations";
import { generateRecommendations } from "@/api/recommendations";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import { format } from "date-fns";
import toast from "react-hot-toast";

export default function RecommendationsPage() {
  const [selectedCalcs, setSelectedCalcs] = useState<number[]>([]);
  const [recommendations, setRecommendations] = useState<any>(null);

  const { data } = useQuery({
    queryKey: ["calculations", { page: 1, limit: 100 }],
    queryFn: () => getCalculations({ page: 1, limit: 100 }),
  });

  const calculations = data?.calculations || [];

  const mutation = useMutation({
    mutationFn: generateRecommendations,
    onSuccess: (data) => {
      setRecommendations(data);
      toast.success("AI recommendations generated!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to generate recommendations");
    },
  });

  const toggleSelection = (id: number) => {
    if (selectedCalcs.includes(id)) {
      setSelectedCalcs(selectedCalcs.filter((c) => c !== id));
    } else if (selectedCalcs.length < 10) {
      setSelectedCalcs([...selectedCalcs, id]);
    } else {
      toast.error("Maximum 10 calculations can be analyzed at once");
    }
  };

  const handleGenerate = () => {
    if (selectedCalcs.length === 0) {
      toast.error("Please select at least one calculation");
      return;
    }
    mutation.mutate({ calculation_ids: selectedCalcs });
  };

  const priorityIcons = {
    high: <AlertTriangle className="w-5 h-5 text-red-600" />,
    medium: <TrendingUp className="w-5 h-5 text-yellow-600" />,
    low: <CheckCircle className="w-5 h-5 text-green-600" />,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI-Powered Cost Recommendations</h1>
        <p className="text-gray-600 mt-1">Get intelligent insights from Claude AI</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Selection Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Select Calculations</CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              Choose up to 10 calculations to analyze
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {calculations.map((calc) => (
                <div
                  key={calc.id}
                  onClick={() => toggleSelection(calc.id)}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedCalcs.includes(calc.id)
                      ? "bg-blue-50 border-blue-500"
                      : "hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">
                        {calc.calc_type} - {format(new Date(calc.created_at), "MMM dd")}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        {calc.cheapest_provider}: ${((calc.aws_total_monthly || 0) + (calc.azure_total_monthly || 0) + (calc.gcp_total_monthly || 0)).toFixed(2)}/mo
                      </p>
                    </div>
                    {selectedCalcs.includes(calc.id) && (
                      <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600 mb-3">
                {selectedCalcs.length} / 10 selected
              </p>
              <Button
                onClick={handleGenerate}
                disabled={mutation.isPending || selectedCalcs.length === 0}
                className="w-full"
              >
                <Lightbulb className="w-4 h-4 mr-2" />
                {mutation.isPending ? "Analyzing..." : "Generate Recommendations"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Recommendations Panel */}
        <div className="lg:col-span-2 space-y-6">
          {!recommendations ? (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                <Lightbulb className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>Select calculations and click "Generate Recommendations" to get AI-powered insights</p>
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{recommendations.summary}</p>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Est. Monthly Savings</p>
                      <p className="text-2xl font-bold text-green-600">
                        ${recommendations.total_estimated_monthly_savings.toFixed(2)}
                      </p>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Est. Annual Savings</p>
                      <p className="text-2xl font-bold text-blue-600">
                        ${recommendations.total_estimated_annual_savings.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Generated on {format(new Date(recommendations.generated_at), "MMM dd, yyyy 'at' HH:mm")}
                  </p>
                </CardContent>
              </Card>

              {recommendations.recommendations.map((rec: any, index: number) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        {priorityIcons[rec.priority as keyof typeof priorityIcons]}
                      </div>
                      <div className="flex-1 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold">{rec.title}</h3>
                            <p className="text-sm text-gray-600">{rec.category}</p>
                          </div>
                          <Badge variant={
                            rec.priority === "high" ? "destructive" :
                            rec.priority === "medium" ? "warning" : "success"
                          }>
                            {rec.priority}
                          </Badge>
                        </div>

                        <p className="text-gray-700">{rec.description}</p>

                        <div className="bg-gray-50 p-3 rounded">
                          <p className="text-sm font-semibold text-gray-700 mb-1">Potential Savings:</p>
                          <p className="text-sm">
                            Monthly: <span className="font-bold text-green-600">${rec.estimated_monthly_savings.toFixed(2)}</span>
                            {" | "}
                            Annual: <span className="font-bold text-green-600">${rec.estimated_annual_savings.toFixed(2)}</span>
                          </p>
                        </div>

                        <div>
                          <p className="text-sm font-semibold text-gray-700 mb-2">Action Steps:</p>
                          <ul className="space-y-1">
                            {rec.action_steps.map((step: string, idx: number) => (
                              <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                                <span className="text-blue-600">•</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {rec.affected_providers.length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">Affects:</span>
                            {rec.affected_providers.map((p: string) => (
                              <Badge key={p} variant="outline">{p}</Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
