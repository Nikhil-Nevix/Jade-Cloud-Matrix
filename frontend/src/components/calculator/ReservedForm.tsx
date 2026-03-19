import React, { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getProviders } from "@/api/providers";
import { getRegions } from "@/api/providers";
import { getReservedPricing, calculateReserved } from "@/api/reserved";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

interface ReservedSelection {
  reserved_pricing_id: number;
  quantity: number;
}

export default function ReservedForm() {
  const [selections, setSelections] = useState<ReservedSelection[]>([{
    reserved_pricing_id: 0,
    quantity: 1,
  }]);
  const [duration, setDuration] = useState(12);
  const [providerId, setProviderId] = useState<number>(0);
  const [regionId, setRegionId] = useState<number>(0);

  const { data: providers } = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });

  const { data: regions } = useQuery({
    queryKey: ["regions", providerId],
    queryFn: () => providerId ? getRegions(providerId) : Promise.resolve([]),
    enabled: !!providerId,
  });

  const { data: pricing } = useQuery({
    queryKey: ["reserved-pricing", providerId, regionId],
    queryFn: () => getReservedPricing({ provider_id: providerId, region_id: regionId }),
    enabled: !!providerId && !!regionId,
  });

  const mutation = useMutation({
    mutationFn: calculateReserved,
    onSuccess: (data) => {
      toast.success("Reserved instance calculation complete!");
      console.log("Reserved results:", data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Calculation failed");
    },
  });

  const addSelection = () => {
    setSelections([...selections, {
      reserved_pricing_id: 0,
      quantity: 1,
    }]);
  };

  const removeSelection = (index: number) => {
    setSelections(selections.filter((_, i) => i !== index));
  };

  const updateSelection = (index: number, field: keyof ReservedSelection, value: any) => {
    const updated = [...selections];
    updated[index] = { ...updated[index], [field]: value };
    setSelections(updated);
  };

  const handleCalculate = () => {
    const valid = selections.every((s) => s.reserved_pricing_id > 0);
    if (!valid) {
      toast.error("Please complete all selections");
      return;
    }
    mutation.mutate({ selections, duration_months: duration });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label>Provider</Label>
          <Select
            value={providerId.toString()}
            onChange={(e) => setProviderId(parseInt(e.target.value))}
            className="mt-1"
          >
            <option value="0">Select Provider</option>
            {providers?.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Region</Label>
          <Select
            value={regionId.toString()}
            onChange={(e) => setRegionId(parseInt(e.target.value))}
            disabled={!providerId}
            className="mt-1"
          >
            <option value="0">Select Region</option>
            {regions?.map((r: any) => (
              <option key={r.id} value={r.id}>{r.region_name}</option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Duration (Months)</Label>
          <Input
            type="number"
            min="1"
            max="36"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value) || 12)}
            className="mt-1"
          />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Reserved Instances</h3>
          <Button variant="outline" size="sm" onClick={addSelection}>
            <Plus className="w-4 h-4 mr-2" />
            Add Instance
          </Button>
        </div>

        {selections.map((selection, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Instance {index + 1}</span>
              {selections.length > 1 && (
                <Button variant="ghost" size="sm" onClick={() => removeSelection(index)}>
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Reserved Instance Plan</Label>
                <Select
                  value={selection.reserved_pricing_id.toString()}
                  onChange={(e) => updateSelection(index, "reserved_pricing_id", parseInt(e.target.value))}
                  disabled={!regionId}
                  className="mt-1"
                >
                  <option value="0">Select Plan</option>
                  {pricing?.map((p: any) => (
                    <option key={p.id} value={p.id}>
                      {p.instance_type} - {p.term} {p.payment_type} (${p.monthly_cost}/mo, {p.savings_vs_ondemand}% savings)
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <Label>Quantity</Label>
                <Input
                  type="number"
                  min="1"
                  value={selection.quantity}
                  onChange={(e) => updateSelection(index, "quantity", parseInt(e.target.value) || 1)}
                  className="mt-1"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <Button onClick={handleCalculate} disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? "Calculating..." : "Calculate Reserved Instance Pricing"}
      </Button>
    </div>
  );
}
