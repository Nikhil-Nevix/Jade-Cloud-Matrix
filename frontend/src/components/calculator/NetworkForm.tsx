import React, { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getProviders } from "@/api/providers";
import { getNetworkPricing, calculateNetwork } from "@/api/network";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

interface NetworkTransfer {
  network_pricing_id: number;
  transfer_gb: number;
}

export default function NetworkForm() {
  const [transfers, setTransfers] = useState<NetworkTransfer[]>([{
    network_pricing_id: 0,
    transfer_gb: 100,
  }]);
  const [duration, setDuration] = useState(12);

  const { data: providers } = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });

  const { data: allNetworkPricing } = useQuery({
    queryKey: ["network-pricing"],
    queryFn: () => getNetworkPricing({}),
  });

  const mutation = useMutation({
    mutationFn: calculateNetwork,
    onSuccess: (data) => {
      toast.success("Network pricing calculation complete!");
      console.log("Network results:", data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Calculation failed");
    },
  });

  const addTransfer = () => {
    setTransfers([...transfers, {
      network_pricing_id: 0,
      transfer_gb: 100,
    }]);
  };

  const removeTransfer = (index: number) => {
    setTransfers(transfers.filter((_, i) => i !== index));
  };

  const updateTransfer = (index: number, field: keyof NetworkTransfer, value: any) => {
    const updated = [...transfers];
    updated[index] = { ...updated[index], [field]: value };
    setTransfers(updated);
  };

  const handleCalculate = () => {
    const valid = transfers.every((t) => t.network_pricing_id > 0 && t.transfer_gb > 0);
    if (!valid) {
      toast.error("Please complete all selections");
      return;
    }
    mutation.mutate({ transfers, duration_months: duration });
  };

  return (
    <div className="space-y-6">
      <div>
        <Label>Duration (Months)</Label>
        <Input
          type="number"
          min="1"
          value={duration}
          onChange={(e) => setDuration(parseInt(e.target.value) || 12)}
          className="mt-1 max-w-xs"
        />
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Data Transfers</h3>
          <Button variant="outline" size="sm" onClick={addTransfer}>
            <Plus className="w-4 h-4 mr-2" />
            Add Transfer
          </Button>
        </div>

        {transfers.map((transfer, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Transfer {index + 1}</span>
              {transfers.length > 1 && (
                <Button variant="ghost" size="sm" onClick={() => removeTransfer(index)}>
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Network Route</Label>
                <Select
                  value={transfer.network_pricing_id.toString()}
                  onChange={(e) => updateTransfer(index, "network_pricing_id", parseInt(e.target.value))}
                  className="mt-1"
                >
                  <option value="0">Select Route</option>
                  {allNetworkPricing?.map((p: any) => (
                    <option key={p.id} value={p.id}>
                      {p.provider_name} - {p.region_code} to {p.destination_type} (${p.price_per_gb}/GB)
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <Label>Transfer Size (GB)</Label>
                <Input
                  type="number"
                  min="1"
                  value={transfer.transfer_gb}
                  onChange={(e) => updateTransfer(index, "transfer_gb", parseFloat(e.target.value) || 100)}
                  className="mt-1"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <Button onClick={handleCalculate} disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? "Calculating..." : "Calculate Network Pricing"}
      </Button>
    </div>
  );
}
