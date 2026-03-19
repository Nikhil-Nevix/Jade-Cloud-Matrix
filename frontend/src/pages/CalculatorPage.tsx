import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ComputeForm from "@/components/calculator/ComputeForm";
import StorageForm from "@/components/calculator/StorageForm";
import ReservedForm from "@/components/calculator/ReservedForm";
import KubernetesForm from "@/components/calculator/KubernetesForm";
import NetworkForm from "@/components/calculator/NetworkForm";
import ResultsPanel from "@/components/calculator/ResultsPanel";

export default function CalculatorPage() {
  const [activeTab, setActiveTab] = useState("standard");
  const [results, setResults] = useState<any>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cloud Cost Calculator</h1>
        <p className="text-gray-600 mt-1">Compare pricing across AWS, Azure, and GCP</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 lg:w-auto">
          <TabsTrigger value="standard">Standard</TabsTrigger>
          <TabsTrigger value="reserved">Reserved</TabsTrigger>
          <TabsTrigger value="kubernetes">Kubernetes</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>

        <TabsContent value="standard" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Standard Compute + Storage Pricing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <ComputeForm />
              <StorageForm />
              <Button className="w-full">Calculate Pricing</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reserved" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Reserved Instances Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <ReservedForm />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kubernetes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Kubernetes Cluster Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <KubernetesForm />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="network" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Network / Data Transfer Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <NetworkForm />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {results && <ResultsPanel results={results} />}
    </div>
  );
}
