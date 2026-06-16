"use client";

import { FormEvent, useState } from "react";
import { apiFetch, friendlyErrorMessage, saveToken } from "@/lib/api";
import type { AuthResponse } from "@/lib/types";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          role: "customer",
        }),
      });
      saveToken(data.access_token);
      setMessage(`${data.user.full_name}님, 회원가입이 완료되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="section">
      <h1>회원가입</h1>
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
            minLength={8}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <label>
          Full name
          <input
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "가입 중" : "Register"}
        </button>
        {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      </form>
    </section>
  );
}
