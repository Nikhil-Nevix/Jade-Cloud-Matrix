import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getProviders } from "@/api/providers";
import { getRegions } from "@/api/providers";
import { getComputePricing } from "@/api/pricing";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";

interface ComputeSelection {
  provider_id: number;
  region_id: number;
  compute_pricing_id: number;
  quantity: number;
}

export default function ComputeForm() {
  const [selections, setSelections] = useState<ComputeSelection[]>([{
    provider_id: 0,
    region_id: 0,
    compute_pricing_id: 0,
    quantity: 1,
  }]);

  const { data: providers } = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });

  const addSelection = () => {
    setSelections([...selections, {
      provider_id: 0,
      region_id: 0,
      compute_pricing_id: 0,
      quantity: 1,
    }]);
  };

  const removeSelection = (index: number) => {
    setSelections(selections.filter((_, i) => i !== index));
  };

  const updateSelection = (index: number, field: keyof ComputeSelection, value: any) => {
    const updated = [...selections];
    updated[index] = { ...updated[index], [field]: value };
    setSelections(updated);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Compute Resources</h3>
        <Button variant="outline" size="sm" onClick={addSelection}>
          <Plus className="w-4 h-4 mr-2" />
          Add Instance
        </Button>
      </div>

      {selections.map((selection, index) => (
        <ComputeSelectionRow
          key={index}
          index={index}
          selection={selection}
          providers={providers || []}
          onChange={updateSelection}
          onRemove={() => removeSelection(index)}
          canRemove={selections.length > 1}
        />
      ))}
    </div>
  );
}

interface ComputeSelectionRowProps {
  index: number;
  selection: ComputeSelection;
  providers: any[];
  onChange: (index: number, field: keyof ComputeSelection, value: any) => void;
  onRemove: () => void;
  canRemove: boolean;
}

function ComputeSelectionRow({ index, selection, providers, onChange, onRemove, canRemove }: ComputeSelectionRowProps) {
  const { data: regions } = useQuery({
    queryKey: ["regions", selection.provider_id],
    queryFn: () => selection.provider_id ? getRegions(selection.provider_id) : Promise.resolve([]),
    enabled: !!selection.provider_id,
  });

  const { data: pricing } = useQuery({
    queryKey: ["compute-pricing", selection.provider_id, selection.region_id],
    queryFn: () => getComputePricing({ provider_id: selection.provider_id, region_id: selection.region_id }),
    enabled: !!selection.provider_id && !!selection.region_id,
  });

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-gray-50">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Instance {index + 1}</span>
        {canRemove && (
          <Button variant="ghost" size="sm" onClick={onRemove}>
            <Trash2 className="w-4 h-4 text-red-500" />
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label>Provider</Label>
          <Select
            value={selection.provider_id.toString()}
            onChange={(e) => onChange(index, "provider_id", parseInt(e.target.value))}
            className="mt-1"
          >
            <option value="0">Select Provider</option>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Region</Label>
          <Select
            value={selection.region_id.toString()}
            onChange={(e) => onChange(index, "region_id", parseInt(e.target.value))}
            disabled={!selection.provider_id}
            className="mt-1"
          >
            <option value="0">Select Region</option>
            {regions?.map((r: any) => (
              <option key={r.id} value={r.id}>{r.region_name}</option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Instance Type</Label>
          <Select
            value={selection.compute_pricing_id.toString()}
            onChange={(e) => onChange(index, "compute_pricing_id", parseInt(e.target.value))}
            disabled={!selection.region_id}
            className="mt-1"
          >
            <option value="0">Select Instance</option>
            {pricing?.map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.instance_type} - {p.vcpu} vCPU, {p.memory_gb} GB RAM (${p.price_per_month}/mo)
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
            onChange={(e) => onChange(index, "quantity", parseInt(e.target.value) || 1)}
            className="mt-1"
          />
        </div>
      </div>
    </div>
  );
}
