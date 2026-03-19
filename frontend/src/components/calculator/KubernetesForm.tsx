import React, { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getProviders } from "@/api/providers";
import { getRegions } from "@/api/providers";
import { getKubernetesPricing, calculateKubernetes } from "@/api/kubernetes";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import toast from "react-hot-toast";

export default function KubernetesForm() {
  const [providerId, setProviderId] = useState<number>(0);
  const [regionId, setRegionId] = useState<number>(0);
  const [nodeTypeId, setNodeTypeId] = useState<number>(0);
  const [nodeCount, setNodeCount] = useState(3);
  const [duration, setDuration] = useState(12);
  const [includeClusterFee, setIncludeClusterFee] = useState(true);

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
    queryKey: ["kubernetes-pricing", providerId, regionId],
    queryFn: () => getKubernetesPricing({ provider_id: providerId, region_id: regionId }),
    enabled: !!providerId && !!regionId,
  });

  const mutation = useMutation({
    mutationFn: calculateKubernetes,
    onSuccess: (data) => {
      toast.success("Kubernetes calculation complete!");
      console.log("Kubernetes results:", data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Calculation failed");
    },
  });

  const handleCalculate = () => {
    if (!providerId || !regionId || !nodeTypeId) {
      toast.error("Please complete all selections");
      return;
    }
    
    mutation.mutate({
      provider_id: providerId,
      region_id: regionId,
      node_type_id: nodeTypeId,
      node_count: nodeCount,
      duration_months: duration,
      include_cluster_fee: includeClusterFee,
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          <Label>Node Type</Label>
          <Select
            value={nodeTypeId.toString()}
            onChange={(e) => setNodeTypeId(parseInt(e.target.value))}
            disabled={!regionId}
            className="mt-1"
          >
            <option value="0">Select Node Type</option>
            {pricing?.map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.node_type} - {p.vcpu} vCPU, {p.memory_gb} GB RAM (${p.price_per_month}/mo)
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Label>Node Count</Label>
          <Input
            type="number"
            min="1"
            value={nodeCount}
            onChange={(e) => setNodeCount(parseInt(e.target.value) || 3)}
            className="mt-1"
          />
        </div>

        <div>
          <Label>Duration (Months)</Label>
          <Input
            type="number"
            min="1"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value) || 12)}
            className="mt-1"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="clusterFee"
            checked={includeClusterFee}
            onChange={(e) => setIncludeClusterFee(e.target.checked)}
            className="w-4 h-4 text-blue-600"
          />
          <Label htmlFor="clusterFee" className="cursor-pointer">
            Include cluster management fee (EKS: $73, GKE: $74/mo)
          </Label>
        </div>
      </div>

      <Button onClick={handleCalculate} disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? "Calculating..." : "Calculate Kubernetes Pricing"}
      </Button>
    </div>
  );
}
