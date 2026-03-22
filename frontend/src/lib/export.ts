export async function exportCalculation(
  calcId: number,
  format: "pdf" | "excel",
  token: string
): Promise<void> {
  const path = format === "pdf" ? "pdf" : "excel";
  const ext = format === "pdf" ? "pdf" : "xlsx";

  const response = await fetch(`/api/v1/export/calculations/${calcId}/${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Export failed");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `jade_report_${calcId}.${ext}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Convenience functions
export async function downloadPDF(calcId: number, token: string): Promise<void> {
  return exportCalculation(calcId, "pdf", token);
}

export async function downloadExcel(calcId: number, token: string): Promise<void> {
  return exportCalculation(calcId, "excel", token);
}
