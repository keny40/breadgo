"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, friendlyErrorMessage, routeForRole, saveAuthSession } from "@/lib/api";
import { GoogleOAuthButton } from "@/components/GoogleOAuthButton";
import type { AuthResponse } from "@/lib/types";

export default function RegisterPage() {
  const router = useRouter();
  const [selectedSignupType, setSelectedSignupType] = useState<"customer" | null>(null);
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
      saveAuthSession(data.access_token, data.user);
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
      <h1>가입 유형을 선택해 주세요</h1>
      <p className="message">
        고객은 바로 회원가입할 수 있고, 상품을 등록하고 판매하려는 가맹점은 입점 신청 후 관리자 승인을 받아야 합니다.
        관리자 계정은 공개 회원가입으로 생성할 수 없습니다.
      </p>
      <div className="signup-choice-grid">
        <button
          type="button"
          className={`signup-choice-card ${selectedSignupType === "customer" ? "selected" : ""}`}
          onClick={() => setSelectedSignupType("customer")}
        >
          <span className="eyebrow">Customer</span>
          <strong>고객으로 가입하기</strong>
          <small>상품을 예약하고 구매하려는 일반 사용자입니다.</small>
        </button>
        <Link className="signup-choice-card" href="/merchant/apply">
          <span className="eyebrow">Merchant</span>
          <strong>가맹점 입점 신청하기</strong>
          <small>상품을 등록하고 판매하려는 매장은 입점 신청 후 관리자 승인을 받아야 합니다.</small>
        </Link>
      </div>

      {!selectedSignupType && (
        <section className="panel">
          <h2>먼저 가입 유형을 선택하세요.</h2>
          <p className="field-help">
            고객 이메일 가입폼과 Google 고객 가입은 `고객으로 가입하기`를 선택한 뒤 표시됩니다.
            가맹점은 이메일/비밀번호로 즉시 가입하지 않고 입점 신청 화면으로 이동합니다.
          </p>
        </section>
      )}

      {selectedSignupType === "customer" && (
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">Customer Signup</p>
          <h2>고객으로 회원가입</h2>
          <p className="field-help">
            상품을 예약하고 구매하려는 일반 사용자용 가입입니다. Google 가입도 고객 전용입니다.
          </p>
        </div>
        <GoogleOAuthButton />
        <p className="message">
          가맹점은 고객 회원가입이 아니라 입점 신청을 진행해 주세요.
        </p>
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
      )}
    </section>
  );
}
