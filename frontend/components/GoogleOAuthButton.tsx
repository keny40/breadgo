"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL, apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { GoogleOAuthStatus } from "@/lib/types";

export function GoogleOAuthButton() {
  const [enabled, setEnabled] = useState(false);
  const [message, setMessage] = useState("Google OAuth 설정을 확인하고 있습니다.");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      try {
        const status = await apiFetch<GoogleOAuthStatus>("/api/v1/auth/google/status");
        if (cancelled) {
          return;
        }
        setEnabled(status.enabled);
        setMessage(
          status.enabled
            ? "Google 계정으로 고객 회원가입 또는 로그인을 진행합니다."
            : "현재 환경에서는 Google OAuth가 꺼져 있습니다. 데모 계정 또는 이메일 로그인을 사용해 주세요.",
        );
      } catch (error) {
        if (cancelled) {
          return;
        }
        setEnabled(false);
        setMessage(friendlyErrorMessage(error));
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  function startGoogleOAuth() {
    window.location.href = `${API_BASE_URL}/api/v1/auth/google/start`;
  }

  return (
    <div className="panel form-grid">
      <button type="button" className="secondary" disabled={loading || !enabled} onClick={startGoogleOAuth}>
        Google로 계속하기
      </button>
      <p className="field-help">{message}</p>
      <p className="field-help">관리자와 가맹점 계정은 별도 승인 방식으로 운영됩니다.</p>
    </div>
  );
}
