"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/api";

export default function NavBar() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    function syncAuth() {
      setLoggedIn(Boolean(getToken()));
    }

    syncAuth();
    window.addEventListener("storage", syncAuth);
    window.addEventListener("breadgo-auth-changed", syncAuth);
    return () => {
      window.removeEventListener("storage", syncAuth);
      window.removeEventListener("breadgo-auth-changed", syncAuth);
    };
  }, []);

  function logout() {
    clearToken();
    setLoggedIn(false);
  }

  return (
    <header className="top-nav">
      <Link href="/" className="brand">
        BreadGo
      </Link>
      <nav className="nav-links" aria-label="Main navigation">
        <Link href="/demo">데모 가이드</Link>
        <Link href="/products">상품 보기</Link>
        <Link href="/my-reservations">내 예약</Link>
        <Link href="/my-payments">내 결제</Link>
        <Link href="/merchant">가맹점</Link>
        <Link href="/merchant/stores">매장</Link>
        <Link href="/merchant/products">상품 관리</Link>
        <Link href="/merchant/pickup">픽업 확인</Link>
        <Link href="/admin">Admin</Link>
      </nav>
      <div className="nav-session">
        {loggedIn ? (
          <>
            <span>로그인됨</span>
            <button type="button" className="secondary nav-button" onClick={logout}>
              로그아웃
            </button>
          </>
        ) : (
          <>
            <Link href="/login">로그인</Link>
            <Link href="/register">회원가입</Link>
          </>
        )}
      </div>
    </header>
  );
}
