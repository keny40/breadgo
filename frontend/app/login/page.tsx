"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, friendlyErrorMessage, routeForRole, saveAuthSession } from "@/lib/api";
import { consumeAuthMessage } from "@/lib/authGuard";
import { GoogleOAuthButton } from "@/components/GoogleOAuthButton";
import type { AuthResponse } from "@/lib/types";

function loginErrorMessage(error: unknown): string {
  const message = friendlyErrorMessage(error);
  const normalized = message.toLowerCase();
  if (
    normalized.includes("invalid") ||
    normalized.includes("incorrect") ||
    normalized.includes("401") ||
    normalized.includes("unauthorized")
  ) {
    return "이메일 또는 비밀번호가 올바르지 않습니다.";
  }
  if (normalized.includes("suspended") || normalized.includes("deactivated") || normalized.includes("inactive")) {
    return "정지 또는 비활성화된 계정입니다. 관리자에게 문의해 주세요.";
  }
  if (normalized.includes("api request failed") || normalized.includes("api base url")) {
    return "로그인 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.";
  }
  return message.includes("\n") ? "로그인 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요." : message;
}

export default function LoginPage() {
  const router = useRouter();
  const [initialAuthMessage] = useState(() => consumeAuthMessage());
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState(initialAuthMessage);
  const [isError, setIsError] = useState(Boolean(initialAuthMessage));
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveAuthSession(data.access_token, data.user);
      setMessage(`${data.user.full_name}님, 로그인되었습니다. 이동합니다.`);
      router.replace(routeForRole(data.user.role));
    } catch (error) {
      setIsError(true);
      setMessage(loginErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="section">
      <h1>로그인</h1>
      <GoogleOAuthButton />
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <label>
          이메일
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "로그인 중" : "로그인"}
        </button>
        {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      </form>
    </section>
  );
}
