"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/api";

export default function NavBar() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { href: "/demo", label: "데모 가이드" },
    { href: "/products", label: "상품 보기" },
    { href: "/my-reservations", label: "내 예약" },
    { href: "/my-payments", label: "내 결제" },
    { href: "/merchant", label: "가맹점" },
    { href: "/merchant/stores", label: "매장" },
    { href: "/merchant/products", label: "상품 관리" },
    { href: "/merchant/pickup", label: "픽업 확인" },
    { href: "/admin", label: "Admin" },
  ];

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
    setMenuOpen(false);
  }

  return (
    <header className="top-nav">
      <Link href="/" className="brand">
        <span className="brand-mark">BG</span>
        <span>BreadGo</span>
      </Link>
      <button
        type="button"
        className="secondary nav-button menu-toggle"
        aria-expanded={menuOpen}
        aria-controls="main-navigation"
        onClick={() => setMenuOpen((current) => !current)}
      >
        메뉴
      </button>
      <nav
        id="main-navigation"
        className={`nav-links ${menuOpen ? "open" : ""}`}
        aria-label="Main navigation"
      >
        {links.map((link) => (
          <Link href={link.href} key={link.href} onClick={() => setMenuOpen(false)}>
            {link.label}
          </Link>
        ))}
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
            <Link href="/login" onClick={() => setMenuOpen(false)}>
              로그인
            </Link>
            <Link href="/register" onClick={() => setMenuOpen(false)}>
              회원가입
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
