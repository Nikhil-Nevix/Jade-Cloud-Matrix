import React from "react";
import WizardContainer from "@/components/wizard/WizardContainer";

export default function CalculatorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Multi-Cloud Cost Comparison</h1>
        <p className="text-gray-600 mt-1">
          Compare pricing across AWS, Azure, and GCP with automatic instance mapping
        </p>
      </div>

      <WizardContainer />
    </div>
  );
}
