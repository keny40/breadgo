"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  apiFetch,
  clearToken,
  getToken,
  routeForRole,
  saveStoredUser,
} from "@/lib/api";
import type { AuthUser } from "@/lib/types";

export type AuthRole = "CUSTOMER" | "MERCHANT" | "ADMIN";

function normalizeRole(role: string | null | undefined): AuthRole | null {
  const normalized = role?.toUpperCase();
  if (normalized === "CUSTOMER" || normalized === "MERCHANT" || normalized === "ADMIN") {
    return normalized;
  }
  return null;
}

function storeAuthMessage(message: string) {
  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("breadgo_auth_message", message);
  }
}

export function useRoleGuard(requiredRole: AuthRole) {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);
  const [message, setMessage] = useState("권한을 확인하고 있습니다.");
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function checkAccess() {
      setAllowed(false);
      setMessage("권한을 확인하고 있습니다.");

      if (!getToken()) {
        const nextMessage = "로그인이 필요합니다.";
        setMessage(nextMessage);
        storeAuthMessage(nextMessage);
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        if (cancelled) return;

        const role = normalizeRole(currentUser.role);
        saveStoredUser(currentUser);
        setUser(currentUser);

        if (role === requiredRole) {
          setAllowed(true);
          setMessage("");
          return;
        }

        const nextMessage = "접근 권한이 없습니다.";
        setMessage(nextMessage);
        storeAuthMessage(nextMessage);
        router.replace(routeForRole(currentUser.role));
      } catch {
        if (cancelled) return;
        const nextMessage = "로그인이 필요합니다.";
        clearToken();
        setUser(null);
        setMessage(nextMessage);
        storeAuthMessage(nextMessage);
        router.replace("/login");
      }
    }

    void checkAccess();
    return () => {
      cancelled = true;
    };
  }, [requiredRole, router]);

  return {
    allowed,
    checking: !allowed,
    message,
    user,
  };
}

export function consumeAuthMessage(): string {
  if (typeof window === "undefined") {
    return "";
  }
  const message = window.sessionStorage.getItem("breadgo_auth_message") || "";
  window.sessionStorage.removeItem("breadgo_auth_message");
  return message;
}
