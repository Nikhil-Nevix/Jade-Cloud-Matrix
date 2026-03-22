import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProviders, getRegions } from "@/api/providers";
import { getStoragePricing } from "@/api/pricing";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, Trash2, HardDrive } from "lucide-react";
import { StorageSelection } from "@/api/wizard";

interface Step2Props {
  selections: StorageSelection[];
  onAdd: () => void;
  onUpdate: (index: number, field: keyof StorageSelection, value: number) => void;
  onRemove: (index: number) => void;
  onBulkUpdate?: (index: number, updates: Partial<StorageSelection>) => void;
}

export default function Step2StorageVolumes({ selections, onAdd, onUpdate, onRemove, onBulkUpdate }: Step2Props) {
  const { data: providers } = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Step 2: Storage Volumes</h2>
        <p className="text-gray-600 mt-2">
          Add block or object storage requirements in GB. This step is optional - you can proceed
          without adding storage if your architecture only requires compute resources.
        </p>
      </div>

      <div className="space-y-4">
        {selections.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
            <HardDrive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No storage volumes added</p>
            <p className="text-sm text-gray-400 mb-4">Storage is optional for this comparison</p>
            <Button onClick={onAdd}>
              <Plus className="w-4 h-4 mr-2" />
              Add Storage Baseline
            </Button>
          </div>
        ) : (
          <>
            {selections.map((selection, index) => (
              <StorageSelectionRow
                key={index}
                index={index}
                selection={selection}
                providers={providers || []}
                onChange={onUpdate}
                onBulkUpdate={onBulkUpdate}
                onRemove={() => onRemove(index)}
              />
            ))}

            <Button variant="outline" className="w-full" onClick={onAdd}>
              <Plus className="w-4 h-4 mr-2" />
              Add Another Volume
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

interface StorageSelectionRowProps {
  index: number;
  selection: StorageSelection;
  providers: any[];
  onChange: (index: number, field: keyof StorageSelection, value: number) => void;
  onBulkUpdate?: (index: number, updates: Partial<StorageSelection>) => void;
  onRemove: () => void;
}

function StorageSelectionRow({ index, selection, providers, onChange, onBulkUpdate, onRemove }: StorageSelectionRowProps) {
  const { data: regions } = useQuery({
    queryKey: ["regions", selection.provider_id],
    queryFn: () => (selection.provider_id ? getRegions(selection.provider_id) : Promise.resolve([])),
    enabled: !!selection.provider_id,
  });

  const { data: pricing } = useQuery({
    queryKey: ["storage-pricing", selection.provider_id, selection.region_id],
    queryFn: () => getStoragePricing({ provider_id: selection.provider_id, region_id: selection.region_id }),
    enabled: !!selection.provider_id && !!selection.region_id,
  });

  const handleProviderChange = (value: string) => {
    const providerId = parseInt(value);
    // Reset region and storage type when provider changes
    if (onBulkUpdate) {
      onBulkUpdate(index, { 
        provider_id: providerId, 
        region_id: 0, 
        storage_pricing_id: 0 
      });
    } else {
      onChange(index, "provider_id", providerId);
      onChange(index, "region_id", 0);
      onChange(index, "storage_pricing_id", 0);
    }
  };

  const handleRegionChange = (value: string) => {
    const regionId = parseInt(value);
    // Reset storage type when region changes
    if (onBulkUpdate) {
      onBulkUpdate(index, { 
        region_id: regionId, 
        storage_pricing_id: 0 
      });
    } else {
      onChange(index, "region_id", regionId);
      onChange(index, "storage_pricing_id", 0);
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-white shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700">Storage Volume {index + 1}</span>
        <Button variant="ghost" size="sm" onClick={onRemove}>
          <Trash2 className="w-4 h-4 text-red-500" />
        </Button>
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
          <Label>Storage Type</Label>
          <Select
            value={selection.storage_pricing_id.toString()}
            onChange={(e) => onChange(index, "storage_pricing_id", parseInt(e.target.value))}
            disabled={!selection.region_id}
            className="mt-1"
          >
            <option value="0">Select Storage Type</option>
            {pricing?.map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.storage_name} ({p.storage_type}) - ${p.price_per_gb_month}/GB/mo
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Size (GB)</Label>
          <Input
            type="number"
            min="1"
            value={selection.size_gb}
            onChange={(e) => onChange(index, "size_gb", parseFloat(e.target.value) || 100)}
            className="mt-1"
            placeholder="e.g., 500"
          />
        </div>
      </div>
    </div>
  );
}
