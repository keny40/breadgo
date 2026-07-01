"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch, friendlyErrorMessage, routeForRole, saveStoredUser, saveToken } from "@/lib/api";
import type { AuthUser } from "@/lib/types";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  const token = searchParams.get("token");
  const [message, setMessage] = useState("");
  const [asyncError, setAsyncError] = useState("");

  useEffect(() => {
    async function finishLogin(nextToken: string) {
      try {
        saveToken(nextToken);
        const user = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        saveStoredUser(user);
        setMessage(`${user.full_name}님, Google 계정으로 로그인되었습니다. 이동합니다.`);
        router.replace(routeForRole(user.role));
      } catch (caught) {
        setAsyncError(friendlyErrorMessage(caught));
      }
    }

    if (error || !token) {
      return;
    }

    void finishLogin(token);
  }, [error, router, token]);

  const visibleError = error || asyncError || (!token ? "Google 로그인 토큰을 찾을 수 없습니다. 다시 시도해 주세요." : "");
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
