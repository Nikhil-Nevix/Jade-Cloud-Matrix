import React from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useWizardState } from "@/hooks/useWizardState";
import { calculateMultiCloudComparison } from "@/api/wizard";
import Step1ComputeInstances from "./Step1ComputeInstances";
import Step2StorageVolumes from "./Step2StorageVolumes";
import Step3Duration from "./Step3Duration";
import Step4Results from "./Step4Results";
import axios from "axios";

export default function WizardContainer() {
  const {
    currentStep,
    computeSelections,
    storageSelections,
    durationMonths,
    results,
    canProceedStep1,
    canProceedStep2,
    canProceedStep3,
    nextStep,
    prevStep,
    goToResults,
    startOver,
    addComputeSelection,
    updateComputeSelection,
    bulkUpdateComputeSelection,
    removeComputeSelection,
    addStorageSelection,
    updateStorageSelection,
    bulkUpdateStorageSelection,
    removeStorageSelection,
    setDurationMonths,
    setResults,
  } = useWizardState();

  // Mutation for calculating costs
  const calculateMutation = useMutation({
    mutationFn: calculateMultiCloudComparison,
    onSuccess: (data) => {
      setResults(data);
      goToResults();
    },
    onError: (error: any) => {
      console.error("Calculation error:", error);
      alert(`Calculation failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleCalculate = () => {
    calculateMutation.mutate({
      compute_selections: computeSelections,
      storage_selections: storageSelections,
      duration_months: durationMonths,
    });
  };

  const handleExportPDF = async () => {
    if (!results) return;
    try {
      const response = await axios.get(`/api/v1/export/pdf/${results.id}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `multicloud-comparison-${results.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("PDF export error:", error);
      alert("Failed to export PDF");
    }
  };

  const handleExportExcel = async () => {
    if (!results) return;
    try {
      const response = await axios.get(`/api/v1/export/excel/${results.id}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `multicloud-comparison-${results.id}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Excel export error:", error);
      alert("Failed to export Excel");
    }
  };

  // Determine if we can proceed to next step
  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return canProceedStep1;
      case 2:
        return canProceedStep2;
      case 3:
        return canProceedStep3;
      default:
        return false;
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Stepper */}
      <div className="flex items-center justify-between max-w-3xl mx-auto">
        {[1, 2, 3, 4].map((step) => (
          <React.Fragment key={step}>
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg
                  ${
                    currentStep === step
                      ? "bg-blue-600 text-white"
                      : currentStep > step
                      ? "bg-green-500 text-white"
                      : "bg-gray-200 text-gray-500"
                  }
                `}
              >
                {step}
              </div>
              <div className="text-xs text-gray-600 mt-2 text-center">
                {step === 1 && "Compute"}
                {step === 2 && "Storage"}
                {step === 3 && "Duration"}
                {step === 4 && "Results"}
              </div>
            </div>
            {step < 4 && (
              <div
                className={`
                  flex-1 h-1 mx-2 rounded
                  ${currentStep > step ? "bg-green-500" : "bg-gray-200"}
                `}
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg border p-8 min-h-[500px]">
        {currentStep === 1 && (
          <Step1ComputeInstances
            selections={computeSelections}
            onAdd={addComputeSelection}
            onUpdate={updateComputeSelection}
            onBulkUpdate={bulkUpdateComputeSelection}
            onRemove={removeComputeSelection}
          />
        )}

        {currentStep === 2 && (
          <Step2StorageVolumes
            selections={storageSelections}
            onAdd={addStorageSelection}
            onUpdate={updateStorageSelection}
            onBulkUpdate={bulkUpdateStorageSelection}
            onRemove={removeStorageSelection}
          />
        )}

        {currentStep === 3 && (
          <Step3Duration
            durationMonths={durationMonths}
            onSelectDuration={setDurationMonths}
            onCalculate={handleCalculate}
            isCalculating={calculateMutation.isPending}
            totalInstances={computeSelections.length}
            totalStorageVolumes={storageSelections.length}
          />
        )}

        {currentStep === 4 && results && (
          <Step4Results
            results={results}
            onStartOver={startOver}
            onExportPDF={handleExportPDF}
            onExportExcel={handleExportExcel}
          />
        )}
      </div>

      {/* Navigation Buttons */}
      {currentStep < 4 && (
        <div className="flex justify-between">
          <Button variant="outline" onClick={prevStep} disabled={currentStep === 1}>
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          {currentStep < 3 && (
            <Button onClick={nextStep} disabled={!canProceed()}>
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
