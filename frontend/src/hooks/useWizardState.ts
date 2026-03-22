import { useState } from "react";
import { ComputeSelection, StorageSelection, MultiCloudCompareResult } from "@/api/wizard";

export interface WizardState {
  currentStep: number;
  computeSelections: ComputeSelection[];
  storageSelections: StorageSelection[];
  durationMonths: number;
  results: MultiCloudCompareResult | null;
}

export function useWizardState() {
  const [currentStep, setCurrentStep] = useState(1);
  const [computeSelections, setComputeSelections] = useState<ComputeSelection[]>([]);
  const [storageSelections, setStorageSelections] = useState<StorageSelection[]>([]);
  const [durationMonths, setDurationMonths] = useState(12);
  const [results, setResults] = useState<MultiCloudCompareResult | null>(null);

  // Validation for each step
  const canProceedStep1 =
    computeSelections.length > 0 &&
    computeSelections.every(s => s.provider_id > 0 && s.region_id > 0 && s.compute_pricing_id > 0);

  const canProceedStep2 = true; // Storage is optional

  const canProceedStep3 = durationMonths > 0;

  // Navigation
  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToResults = () => {
    setCurrentStep(4);
  };

  const startOver = () => {
    setCurrentStep(1);
    setComputeSelections([]);
    setStorageSelections([]);
    setDurationMonths(12);
    setResults(null);
  };

  // Compute management
  const addComputeSelection = () => {
    setComputeSelections([
      ...computeSelections,
      {
        provider_id: 0,
        region_id: 0,
        compute_pricing_id: 0,
        quantity: 1,
      },
    ]);
  };

  const updateComputeSelection = (index: number, field: keyof ComputeSelection, value: number) => {
    const updated = [...computeSelections];
    updated[index] = { ...updated[index], [field]: value };
    setComputeSelections(updated);
  };

  const bulkUpdateComputeSelection = (index: number, updates: Partial<ComputeSelection>) => {
    const updated = [...computeSelections];
    updated[index] = { ...updated[index], ...updates };
    setComputeSelections(updated);
  };

  const removeComputeSelection = (index: number) => {
    setComputeSelections(computeSelections.filter((_, i) => i !== index));
  };

  // Storage management
  const addStorageSelection = () => {
    setStorageSelections([
      ...storageSelections,
      {
        provider_id: 0,
        region_id: 0,
        storage_pricing_id: 0,
        size_gb: 100,
      },
    ]);
  };

  const updateStorageSelection = (index: number, field: keyof StorageSelection, value: number) => {
    const updated = [...storageSelections];
    updated[index] = { ...updated[index], [field]: value };
    setStorageSelections(updated);
  };

  const bulkUpdateStorageSelection = (index: number, updates: Partial<StorageSelection>) => {
    const updated = [...storageSelections];
    updated[index] = { ...updated[index], ...updates };
    setStorageSelections(updated);
  };

  const removeStorageSelection = (index: number) => {
    setStorageSelections(storageSelections.filter((_, i) => i !== index));
  };

  return {
    // State
    currentStep,
    computeSelections,
    storageSelections,
    durationMonths,
    results,

    // Validation
    canProceedStep1,
    canProceedStep2,
    canProceedStep3,

    // Navigation
    nextStep,
    prevStep,
    goToResults,
    startOver,
    setCurrentStep,

    // Compute
    addComputeSelection,
    updateComputeSelection,
    bulkUpdateComputeSelection,
    removeComputeSelection,

    // Storage
    addStorageSelection,
    updateStorageSelection,
    bulkUpdateStorageSelection,
    removeStorageSelection,

    // Duration
    setDurationMonths,

    // Results
    setResults,
  };
}
