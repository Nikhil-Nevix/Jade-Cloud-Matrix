import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { getCalculations, deleteCalculation } from "@/api/calculations";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Trash2, Download, FileText, ChevronLeft, ChevronRight, Filter } from "lucide-react";
import { format } from "date-fns";
import { downloadPDF, downloadExcel } from "@/lib/export";
import toast from "react-hot-toast";

export default function HistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);

  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "20");
  const calcType = searchParams.get("calc_type") || "";
  const provider = searchParams.get("provider") || "";
  const fromDate = searchParams.get("from_date") || "";
  const toDate = searchParams.get("to_date") || "";
  const minCost = searchParams.get("min_cost") || "";
  const maxCost = searchParams.get("max_cost") || "";

  const { data, refetch } = useQuery({
    queryKey: ["calculations", { page, limit, calc_type: calcType, provider, from_date: fromDate, to_date: toDate, min_cost: minCost, max_cost: maxCost }],
    queryFn: () => getCalculations({ 
      page, 
      limit, 
      calc_type: calcType || undefined,
      provider: provider || undefined,
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
      min_cost: minCost ? parseFloat(minCost) : undefined,
      max_cost: maxCost ? parseFloat(maxCost) : undefined,
    }),
  });

  const calculations = data?.calculations || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this calculation?")) return;
    try {
      await deleteCalculation(id);
      toast.success("Calculation deleted");
      refetch();
    } catch (error) {
      toast.error("Failed to delete calculation");
    }
  };

  const updateFilter = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    newParams.set("page", "1");
    setSearchParams(newParams);
  };

  const resetFilters = () => {
    setSearchParams({ page: "1", limit: "20" });
  };

  const goToPage = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set("page", newPage.toString());
    setSearchParams(newParams);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calculation History</h1>
          <p className="text-gray-600 mt-1">{total} total calculations</p>
        </div>
        <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
          <Filter className="w-4 h-4 mr-2" />
          {showFilters ? "Hide Filters" : "Show Filters"}
        </Button>
      </div>

      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle>Advanced Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Calculation Type</Label>
                <Select
                  value={calcType}
                  onChange={(e) => updateFilter("calc_type", e.target.value)}
                  className="mt-1"
                >
                  <option value="">All Types</option>
                  <option value="standard">Standard</option>
                  <option value="reserved">Reserved</option>
                  <option value="kubernetes">Kubernetes</option>
                  <option value="network">Network</option>
                </Select>
              </div>

              <div>
                <Label>Provider</Label>
                <Select
                  value={provider}
                  onChange={(e) => updateFilter("provider", e.target.value)}
                  className="mt-1"
                >
                  <option value="">All Providers</option>
                  <option value="AWS">AWS</option>
                  <option value="Azure">Azure</option>
                  <option value="GCP">GCP</option>
                </Select>
              </div>

              <div>
                <Label>From Date</Label>
                <Input
                  type="date"
                  value={fromDate}
                  onChange={(e) => updateFilter("from_date", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label>To Date</Label>
                <Input
                  type="date"
                  value={toDate}
                  onChange={(e) => updateFilter("to_date", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label>Min Cost (Monthly)</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={minCost}
                  onChange={(e) => updateFilter("min_cost", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label>Max Cost (Monthly)</Label>
                <Input
                  type="number"
                  placeholder="Unlimited"
                  value={maxCost}
                  onChange={(e) => updateFilter("max_cost", e.target.value)}
                  className="mt-1"
                />
              </div>
            </div>

            <div className="mt-4">
              <Button variant="outline" onClick={resetFilters}>
                Reset Filters
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Cheapest</TableHead>
                <TableHead>AWS</TableHead>
                <TableHead>Azure</TableHead>
                <TableHead>GCP</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {calculations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No calculations found
                  </TableCell>
                </TableRow>
              ) : (
                calculations.map((calc) => (
                  <TableRow key={calc.id}>
                    <TableCell>{format(new Date(calc.created_at), "MMM dd, yyyy")}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{calc.calc_type}</Badge>
                    </TableCell>
                    <TableCell>{calc.duration_months} mo</TableCell>
                    <TableCell>
                      {calc.cheapest_provider && (
                        <Badge variant="success">{calc.cheapest_provider}</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {calc.aws_total_monthly ? `$${calc.aws_total_monthly.toFixed(2)}` : "-"}
                    </TableCell>
                    <TableCell>
                      {calc.azure_total_monthly ? `$${calc.azure_total_monthly.toFixed(2)}` : "-"}
                    </TableCell>
                    <TableCell>
                      {calc.gcp_total_monthly ? `$${calc.gcp_total_monthly.toFixed(2)}` : "-"}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={() => downloadPDF(calc.id)}>
                          <FileText className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => downloadExcel(calc.id)}>
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(calc.id)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Page {page} of {totalPages} ({total} total)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(page - 1)}
              disabled={page === 1}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(page + 1)}
              disabled={page === totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
