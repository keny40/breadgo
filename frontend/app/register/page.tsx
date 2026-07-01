"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, friendlyErrorMessage, routeForRole, saveStoredUser, saveToken } from "@/lib/api";
import { GoogleOAuthButton } from "@/components/GoogleOAuthButton";
import type { AuthResponse } from "@/lib/types";

export default function RegisterPage() {
  const router = useRouter();
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
      saveStoredUser(data.user);
      setMessage(`${data.user.full_name}님, 회원가입이 완료되었습니다. 이동합니다.`);
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
      <h1>고객 회원가입</h1>
      <p className="message">
        고객으로 가입하고 마감 할인 상품을 예약하세요. 관리자 계정은 공개 회원가입으로 생성할 수 없습니다.
        가맹점은 입점 신청 후 관리자 승인 절차를 거칩니다.
      </p>
      <GoogleOAuthButton />
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>이메일로 고객 가입</h2>
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
          {loading ? "가입 중" : "고객 회원가입"}
        </button>
        {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      </form>
      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Merchant Application</p>
            <h2>가맹점 입점 신청</h2>
            <p>가맹점은 자동 가입되지 않으며, 입점 신청 후 관리자 승인 절차를 거칩니다.</p>
          </div>
          <Link className="button-link secondary" href="/merchant/apply">
            입점 신청하기
          </Link>
        </div>
      </section>
    </section>
  );
}
