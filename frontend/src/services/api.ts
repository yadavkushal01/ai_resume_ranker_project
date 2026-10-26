import type { BackendStatus, BatchResponse, ImprovedResume } from "@/types/ranking";
const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
export class ApiRequestError extends Error {
  constructor(message: string, readonly code: "http" | "network" | "timeout" | "invalid_response", readonly status?: number) { super(message); this.name = "ApiRequestError"; }
}
export async function checkBackend(): Promise<BackendStatus> {
  try {
    const response = await fetch(`${API_URL}/`, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new ApiRequestError(`Backend health check failed (${response.status}).`, "http", response.status);
    return await response.json() as BackendStatus;
  } catch (error) { if (error instanceof ApiRequestError) throw error; throw new ApiRequestError("Unable to reach FastAPI. Confirm the backend is running.", "network"); }
}
function detailFrom(text: string): string { try { return (JSON.parse(text) as { detail?: string }).detail || text; } catch { return text; } }
function postForm<T>(path: string, formData: FormData, timeout = 300_000): Promise<T> {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest(); request.open("POST", `${API_URL}${path}`); request.timeout = timeout; request.responseType = "text";
    request.onerror = () => reject(new ApiRequestError("Unable to reach the backend. Confirm FastAPI is running.", "network"));
    request.ontimeout = () => reject(new ApiRequestError("Request timed out. The first model run can take longer while it downloads.", "timeout"));
    request.onload = () => {
      if (request.status < 200 || request.status >= 300) { reject(new ApiRequestError(detailFrom(request.responseText) || `Backend request failed (${request.status}).`, "http", request.status)); return; }
      try { resolve(JSON.parse(request.responseText) as T); } catch { reject(new ApiRequestError("Backend returned invalid JSON.", "invalid_response")); }
    };
    request.send(formData);
  });
}
export function analyzeResumes(jobDescription: string, files: File[]): Promise<BatchResponse> {
  const form = new FormData(); form.append("job_description", jobDescription); files.forEach(file => form.append("resumes", file));
  return postForm<BatchResponse>("/analyze-batch", form, 600_000);
}
export function improveResume(jobDescription: string, file: File): Promise<ImprovedResume> {
  const form = new FormData(); form.append("job_description", jobDescription); form.append("resume", file);
  return postForm<ImprovedResume>("/improve-resume", form, 600_000);
}
