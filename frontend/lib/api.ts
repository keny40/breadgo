export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type ApiError = {
  detail?: string;
};

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("access_token");
}

export function hasToken(): boolean {
  return Boolean(getToken());
}

export function saveToken(token: string): void {
  window.localStorage.setItem("access_token", token);
  window.dispatchEvent(new Event("breadgo-auth-changed"));
}

export function clearToken(): void {
  window.localStorage.removeItem("access_token");
  window.dispatchEvent(new Event("breadgo-auth-changed"));
}

export function friendlyErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : "요청 처리에 실패했습니다.";
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes("authentication") || lowerMessage.includes("not authenticated")) {
    return "로그인이 필요합니다.";
  }
  if (lowerMessage.includes("merchant profile")) {
    return "가맹점 등록이 필요합니다.";
  }
  if (lowerMessage.includes("insufficient product quantity")) {
    return "예약 가능한 수량이 부족합니다.";
  }
  if (lowerMessage.includes("pickup code")) {
    return "픽업코드를 찾을 수 없습니다.";
  }
  if (lowerMessage.includes("not found")) {
    return "요청한 정보를 찾을 수 없습니다.";
  }
  return message;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false,
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  const token = getToken();
  if (requireAuth && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (requireAuth && !token) {
    throw new Error("로그인이 필요합니다.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const error = (await response.json()) as ApiError;
      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}
