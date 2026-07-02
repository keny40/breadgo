"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch, clearToken, friendlyErrorMessage, routeForRole, saveAuthSession, saveToken } from "@/lib/api";
import type { AuthUser } from "@/lib/types";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  const token = searchParams.get("token");
  const [message, setMessage] = useState("");
  const [asyncError, setAsyncError] = useState("");

  function googleCallbackErrorMessage(rawError: string): string {
    const lowerError = rawError.toLowerCase();

    if (lowerError.includes("cancelled") || lowerError.includes("denied")) {
      return "Google 로그인이 취소되었습니다. 다시 시도해 주세요.";
    }
    if (lowerError.includes("authorization code")) {
      return "Google 로그인 인증 코드가 전달되지 않았습니다. 다시 시도해 주세요.";
    }
    if (lowerError.includes("verified")) {
      return "Google 계정 이메일 인증이 필요합니다.";
    }
    if (lowerError.includes("customer")) {
      return "Google 로그인은 고객 계정에서만 사용할 수 있습니다. 관리자와 가맹점 계정은 이메일 로그인을 사용해 주세요.";
    }
    return "Google 로그인에 실패했습니다. 잠시 후 다시 시도해 주세요.";
  }

  useEffect(() => {
    async function finishLogin(nextToken: string) {
      try {
        saveToken(nextToken);
        const user = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        if (user.role?.toLowerCase() !== "customer") {
          clearToken();
          setAsyncError("Google 로그인은 고객 계정에서만 사용할 수 있습니다. 관리자와 가맹점 계정은 이메일 로그인을 사용해 주세요.");
          return;
        }
        saveAuthSession(nextToken, user);
        setMessage(`${user.full_name}님, Google 계정으로 로그인되었습니다. 이동합니다.`);
        router.replace(routeForRole(user.role));
      } catch (caught) {
        clearToken();
        const nextMessage = friendlyErrorMessage(caught);
        setAsyncError(
          nextMessage === "로그인이 필요합니다."
            ? "Google 로그인 세션을 저장하지 못했습니다. 다시 시도해 주세요."
            : nextMessage,
        );
      }
    }

    if (error || !token) {
      return;
    }

    void finishLogin(token);
  }, [error, router, token]);

  const visibleError =
    (error ? googleCallbackErrorMessage(error) : "") ||
    asyncError ||
    (!token ? "Google 로그인 토큰을 찾을 수 없습니다. 다시 시도해 주세요." : "");
  const visibleMessage = visibleError || message || "Google 로그인 결과를 확인하고 있습니다.";

  return (
    <section className="section">
      <h1>Google 로그인</h1>
      <div className={`message ${visibleError ? "error" : "success"}`}>{visibleMessage}</div>
    </section>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={<section className="section"><p className="message">Google 로그인 결과를 확인하고 있습니다.</p></section>}>
      <GoogleCallbackContent />
    </Suspense>
  );
}
