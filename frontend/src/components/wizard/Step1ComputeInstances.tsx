import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProviders, getRegions } from "@/api/providers";
import { getComputePricing } from "@/api/pricing";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import { ComputeSelection } from "@/api/wizard";

interface Step1Props {
  selections: ComputeSelection[];
  onAdd: () => void;
  onUpdate: (index: number, field: keyof ComputeSelection, value: number) => void;
  onRemove: (index: number) => void;
  onBulkUpdate?: (index: number, updates: Partial<ComputeSelection>) => void;
}

export default function Step1ComputeInstances({ selections, onAdd, onUpdate, onRemove, onBulkUpdate }: Step1Props) {
  const { data: providers } = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Step 1: Compute Instances</h2>
        <p className="text-gray-600 mt-2">
          Select your baseline compute instances from any provider. The wizard will automatically
          find equivalent instances across AWS, Azure, and GCP for cost comparison.
        </p>
      </div>

      <div className="space-y-4">
        {selections.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
            <p className="text-gray-500 mb-4">No compute instances added yet</p>
            <Button onClick={onAdd}>
              <Plus className="w-4 h-4 mr-2" />
              Add Baseline Instance
            </Button>
          </div>
        ) : (
          <>
            {selections.map((selection, index) => (
              <ComputeSelectionRow
                key={index}
                index={index}
                selection={selection}
                providers={providers || []}
                onChange={onUpdate}
                onBulkUpdate={onBulkUpdate}
                onRemove={() => onRemove(index)}
                canRemove={selections.length > 1}
              />
            ))}

            <Button variant="outline" className="w-full" onClick={onAdd}>
              <Plus className="w-4 h-4 mr-2" />
              Add Another Instance
            </Button>
          </>
        )}
      </div>

      {selections.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Auto-Mapping:</strong> For each instance you add, the wizard will find equivalent
            instance types across all providers (AWS, Azure, GCP) based on vCPU and memory specs.
          </p>
        </div>
      )}
    </div>
  );
}

interface ComputeSelectionRowProps {
  index: number;
  selection: ComputeSelection;
  providers: any[];
  onChange: (index: number, field: keyof ComputeSelection, value: number) => void;
  onBulkUpdate?: (index: number, updates: Partial<ComputeSelection>) => void;
  onRemove: () => void;
  canRemove: boolean;
}

function ComputeSelectionRow({ index, selection, providers, onChange, onBulkUpdate, onRemove, canRemove }: ComputeSelectionRowProps) {
  const { data: regions } = useQuery({
    queryKey: ["regions", selection.provider_id],
    queryFn: () => (selection.provider_id ? getRegions(selection.provider_id) : Promise.resolve([])),
    enabled: !!selection.provider_id,
  });

  const { data: pricing } = useQuery({
    queryKey: ["compute-pricing", selection.provider_id, selection.region_id],
    queryFn: () => getComputePricing({ provider_id: selection.provider_id, region_id: selection.region_id }),
    enabled: !!selection.provider_id && !!selection.region_id,
  });

  const handleProviderChange = (value: string) => {
    const providerId = parseInt(value);
    // Reset region and instance when provider changes
    if (onBulkUpdate) {
      onBulkUpdate(index, { 
        provider_id: providerId, 
        region_id: 0, 
        compute_pricing_id: 0 
      });
    } else {
      onChange(index, "provider_id", providerId);
      onChange(index, "region_id", 0);
      onChange(index, "compute_pricing_id", 0);
    }
  };

  const handleRegionChange = (value: string) => {
    const regionId = parseInt(value);
    // Reset instance when region changes
    if (onBulkUpdate) {
      onBulkUpdate(index, { 
        region_id: regionId, 
        compute_pricing_id: 0 
      });
    } else {
      onChange(index, "region_id", regionId);
      onChange(index, "compute_pricing_id", 0);
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-white shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700">Baseline Instance {index + 1}</span>
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
            onChange={(e) => handleProviderChange(e.target.value)}
            className="mt-1"
          >
            <option value="0">Select Provider</option>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Region</Label>
          <Select
            value={selection.region_id.toString()}
            onChange={(e) => handleRegionChange(e.target.value)}
            disabled={!selection.provider_id}
            className="mt-1"
          >
            <option value="0">Select Region</option>
            {regions?.map((r: any) => (
              <option key={r.id} value={r.id}>
                {r.region_name}
              </option>
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
                {p.instance_type} - {p.vcpu} vCPU, {p.memory_gb} GB RAM (${p.price_per_month.toFixed(2)}/mo)
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Number of Instances</Label>
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
