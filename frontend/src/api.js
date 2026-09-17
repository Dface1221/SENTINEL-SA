const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchDashboard() {
  const res = await fetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  return res.json();
}

export async function fetchCSEs() {
  const res = await fetch(`${API_BASE}/cses`);
  if (!res.ok) throw new Error("Failed to fetch CSE list");
  return res.json();
}

export async function fetchCSEProfile(cseId) {
  const res = await fetch(`${API_BASE}/cses/${cseId}`);
  if (!res.ok) throw new Error(`Failed to fetch profile for ${cseId}`);
  return res.json();
}

export async function fetchFindings(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/findings?${query}`);
  if (!res.ok) throw new Error("Failed to fetch findings");
  return res.json();
}

export async function fetchFindingDetail(findingId) {
  const res = await fetch(`${API_BASE}/findings/${findingId}`);
  if (!res.ok) throw new Error(`Failed to fetch finding ${findingId}`);
  return res.json();
}

export async function updateFindingStatus(findingId, status, notes = "") {
  const res = await fetch(`${API_BASE}/findings/${findingId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, supervisor_notes: notes })
  });
  if (!res.ok) throw new Error("Failed to update status");
  return res.json();
}

export async function fetchReviewQueue() {
  const res = await fetch(`${API_BASE}/review-queue`);
  if (!res.ok) throw new Error("Failed to fetch review queue");
  return res.json();
}

export async function fetchSamples() {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) throw new Error("Failed to fetch recommended samples");
  return res.json();
}

export async function fetchNegativeSpaceMatrix() {
  const res = await fetch(`${API_BASE}/negative-space`);
  if (!res.ok) throw new Error("Failed to fetch negative space matrix");
  return res.json();
}

export async function fetchBenchmarks() {
  const res = await fetch(`${API_BASE}/benchmarks`);
  if (!res.ok) throw new Error("Failed to fetch benchmarks");
  return res.json();
}

export async function fetchRemediations(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/remediations?${query}`);
  if (!res.ok) throw new Error("Failed to fetch remediations");
  return res.json();
}

export async function createRemediation(data) {
  const res = await fetch(`${API_BASE}/remediations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("Failed to create remediation");
  return res.json();
}

export async function updateRemediation(actionId, data) {
  const res = await fetch(`${API_BASE}/remediations/${actionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("Failed to update remediation");
  return res.json();
}

export async function fetchValidation() {
  const res = await fetch(`${API_BASE}/validation`);
  if (!res.ok) throw new Error("Failed to fetch validation metrics");
  return res.json();
}

export async function generateDemoData() {
  const res = await fetch(`${API_BASE}/demo/generate`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to generate demo dataset");
  return res.json();
}

export async function runSupervisoryAnalysis() {
  const res = await fetch(`${API_BASE}/analytics/run`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to run supervisory analysis");
  return res.json();
}

export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData
  });
  return res.json();
}

export async function fetchAuditLogs() {
  const res = await fetch(`${API_BASE}/audit-logs`);
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export function getExecutiveReportUrl() {
  return `${API_BASE}/reports/executive`;
}

export function getCSEReportUrl(cseId) {
  return `${API_BASE}/reports/cse/${cseId}`;
}
