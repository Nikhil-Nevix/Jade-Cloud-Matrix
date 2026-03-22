import React from "react";
import { Button } from "@/components/ui/button";
import { Calculator, Loader2 } from "lucide-react";

interface Step3Props {
  durationMonths: number;
  onSelectDuration: (months: number) => void;
  onCalculate: () => void;
  isCalculating: boolean;
  totalInstances: number;
  totalStorageVolumes: number;
}

const DURATION_OPTIONS = [
  { months: 1, label: "1 Month" },
  { months: 3, label: "3 Months" },
  { months: 6, label: "6 Months" },
  { months: 12, label: "12 Months" },
  { months: 24, label: "24 Months" },
  { months: 36, label: "36 Months" },
];

export default function Step3Duration({
  durationMonths,
  onSelectDuration,
  onCalculate,
  isCalculating,
  totalInstances,
  totalStorageVolumes,
}: Step3Props) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Step 3: Commitment Duration</h2>
        <p className="text-gray-600 mt-2">
          Select the expected lifespan for this architecture to calculate long-term costs.
        </p>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Select Duration</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {DURATION_OPTIONS.map((option) => (
            <button
              key={option.months}
              onClick={() => onSelectDuration(option.months)}
              className={`
                p-6 rounded-lg border-2 transition-all
                ${
                  durationMonths === option.months
                    ? "border-blue-500 bg-blue-50 shadow-md"
                    : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                }
              `}
            >
              <div className="text-2xl font-bold text-gray-900">{option.months}</div>
              <div className="text-sm text-gray-600 mt-1">{option.months === 1 ? "Month" : "Months"}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ready to analyze?</h3>
        <div className="space-y-2 mb-6">
          <div className="flex items-center text-gray-700">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
            <span>
              <strong>{totalInstances}</strong> Compute instance{totalInstances !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="flex items-center text-gray-700">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
            <span>
              <strong>{totalStorageVolumes}</strong> Storage volume{totalStorageVolumes !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="flex items-center text-gray-700">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
            <span>
              <strong>{durationMonths}</strong> Month{durationMonths !== 1 ? "s" : ""} commitment
            </span>
          </div>
        </div>

        <Button
          onClick={onCalculate}
          disabled={isCalculating || totalInstances === 0}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg font-semibold"
          size="lg"
        >
          {isCalculating ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Calculating Costs...
            </>
          ) : (
            <>
              <Calculator className="w-5 h-5 mr-2" />
              Calculate Multi-Cloud Costs
            </>
          )}
        </Button>
      </div>

      {totalInstances === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            Please add at least one compute instance in Step 1 before calculating costs.
          </p>
        </div>
      )}
    </div>
  );
}
