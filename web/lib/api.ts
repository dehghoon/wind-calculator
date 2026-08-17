export type ApiError = {
  status: number;
  code: string;
  message: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    throw {
      status: response.status,
      code: typeof detail?.code === "string" ? detail.code : `HTTP_${response.status}`,
      message:
        typeof detail?.message === "string"
          ? detail.message
          : `Request failed with status ${response.status}.`,
    } satisfies ApiError;
  }

  return (await response.json()) as T;
}

export async function getCapabilities(): Promise<{
  routes: string[];
  code_editions: string[];
  limitations: string[];
}> {
  return apiRequest("/api/v1/capabilities", { cache: "no-store" });
}
