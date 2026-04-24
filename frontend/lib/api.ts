import type {
  AppSettings,
  CashDocument,
  ImportResponse,
  ValidationErrorSummary,
} from "../components/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return (await response.json()) as T;
}

export async function getSettings(): Promise<AppSettings> {
  return parseJson<AppSettings>(
    await fetch(`${API_BASE_URL}/api/settings`, { cache: "no-store" }),
  );
}

export async function listDocuments(
  searchParams?: URLSearchParams,
): Promise<CashDocument[]> {
  const suffix = searchParams ? `?${searchParams.toString()}` : "";
  return parseJson<CashDocument[]>(
    await fetch(`${API_BASE_URL}/api/documents${suffix}`, { cache: "no-store" }),
  );
}

export async function listValidationErrors(): Promise<ValidationErrorSummary[]> {
  return parseJson<ValidationErrorSummary[]>(
    await fetch(`${API_BASE_URL}/api/documents/validation-errors`, { cache: "no-store" }),
  );
}

export async function importSaldeo(file: File): Promise<ImportResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/imports/saldeo`, {
    method: "POST",
    body: formData,
  });
  return parseJson<ImportResponse>(response);
}

export async function importBank(file: File): Promise<ImportResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/imports/bank`, {
    method: "POST",
    body: formData,
  });
  return parseJson<ImportResponse>(response);
}
