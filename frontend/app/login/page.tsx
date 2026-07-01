"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, friendlyErrorMessage, routeForRole, saveAuthSession } from "@/lib/api";
import { consumeAuthMessage } from "@/lib/authGuard";
import { GoogleOAuthButton } from "@/components/GoogleOAuthButton";
import type { AuthResponse } from "@/lib/types";

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
      setMessage(friendlyErrorMessage(error));
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
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "로그인 중" : "Login"}
        </button>
        {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      </form>
    </section>
  );
}
