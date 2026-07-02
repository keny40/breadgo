"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiFetch, clearToken, getStoredUser, getToken, saveStoredUser } from "@/lib/api";
import type { AuthUser, MerchantProWeeklyReportUnreadCount, Notification } from "@/lib/types";

export default function NavBar() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [weeklyReportUnreadCount, setWeeklyReportUnreadCount] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  const normalizedRole = userRole?.toLowerCase();
  const customerLinks = [
    { href: "/products", label: "상품 보기" },
    { href: "/my-reservations", label: "내 예약" },
    { href: "/my-payments", label: "내 결제" },
  ];
  const roleLinks = !loggedIn
    ? [{ href: "/products", label: "상품 보기" }]
    : normalizedRole === "merchant"
      ? [
          { href: "/merchant", label: "가맹점 홈" },
          { href: "/merchant/products", label: "상품관리" },
          { href: "/merchant/orders", label: "주문관리" },
          { href: "/merchant/pickup", label: "픽업" },
          { href: "/merchant/pro/pos", label: "POS" },
          { href: "/merchant/pro/inventory-ledger", label: "재고 이력" },
          { href: "/merchant/pro", label: "Pro 대시보드" },
          { href: "/merchant/pro/daily-brief", label: "오늘 브리프" },
          { href: "/merchant/pro/weekly-report", label: "주간 리포트" },
          {
            href: "/merchant/pro/weekly-report-notifications",
            label:
              weeklyReportUnreadCount > 0
                ? `리포트 알림 ${weeklyReportUnreadCount}`
                : "리포트 알림",
          },
          { href: "/merchant/pro/plan", label: "Pro 플랜" },
          { href: "/merchant/pro/stores", label: "매장 통합" },
          { href: "/merchant/pro/recommendations", label: "Pro 추천" },
          { href: "/merchant/pro/recommendation-performance", label: "추천 성과" },
          { href: "/merchant/pro/product-funnel", label: "고객 전환" },
          { href: "/merchant/pro/esg", label: "ESG 리포트" },
          { href: "/merchant/pro/inventory-alerts", label: "재고 알림" },
          { href: "/merchant/stores", label: "매장" },
          { href: "/merchant/products/import", label: "CSV 등록" },
          { href: "/merchant/product-templates", label: "상품 템플릿" },
          { href: "/merchant/settlement-account", label: "정산 계좌" },
          { href: "/merchant/settlements", label: "정산 내역" },
        ]
      : normalizedRole === "admin"
        ? [
            { href: "/admin", label: "Admin" },
            { href: "/admin/settlements", label: "정산 관리" },
            { href: "/admin/ops", label: "운영 점검" },
            { href: "/admin/pro/operations", label: "Pro 운영" },
            { href: "/admin/pro/operations/health-alerts", label: "Pro 상태 알림" },
            { href: "/admin/pro/operations/audit-logs", label: "Pro 감사 로그" },
            { href: "/admin/pro/weekly-report-batches", label: "Batch Monitor" },
            { href: "/admin/pro/weekly-report-deliveries", label: "Delivery Preview" },
          ]
        : normalizedRole === "customer"
          ? customerLinks
          : [];
  const links = [
    { href: "/demo", label: "데모 가이드" },
    ...(loggedIn ? [{ href: "/notifications", label: unreadCount > 0 ? `알림 ${unreadCount}` : "알림" }] : []),
    ...roleLinks,
  ];

  useEffect(() => {
    function syncAuth() {
      const token = getToken();
      const storedUser = getStoredUser();
      setLoggedIn(Boolean(token));
      setUserEmail(storedUser?.email || null);
      setUserRole(storedUser?.role || null);
      if (!token) {
        setUnreadCount(0);
        setWeeklyReportUnreadCount(0);
      }

      if (token && (!storedUser?.email || !storedUser?.role)) {
        void apiFetch<AuthUser>("/api/v1/auth/me", {}, true)
          .then((user) => {
            saveStoredUser(user);
            setUserEmail(user.email || null);
            setUserRole(user.role || null);
            if (user.role?.toLowerCase() === "merchant") {
              void apiFetch<MerchantProWeeklyReportUnreadCount>(
                "/api/v1/merchant/pro/weekly-report/notifications/unread-count",
                {},
                true,
              )
                .then((result) => {
                  setWeeklyReportUnreadCount(result.unread_count);
                })
                .catch(() => {
                  setWeeklyReportUnreadCount(0);
                });
            }
          })
          .catch(() => {
            setUserEmail(null);
            setUserRole(null);
          });
      }

      if (token) {
        void apiFetch<Notification[]>("/api/v1/notifications/me", {}, true)
          .then((notifications) => {
            setUnreadCount(notifications.filter((notification) => !notification.is_read).length);
          })
          .catch(() => {
            setUnreadCount(0);
          });

        if (storedUser?.role?.toLowerCase() === "merchant") {
          void apiFetch<MerchantProWeeklyReportUnreadCount>(
            "/api/v1/merchant/pro/weekly-report/notifications/unread-count",
            {},
            true,
          )
            .then((result) => {
              setWeeklyReportUnreadCount(result.unread_count);
            })
            .catch(() => {
              setWeeklyReportUnreadCount(0);
            });
        } else {
          setWeeklyReportUnreadCount(0);
        }
      }
    }

    syncAuth();
    window.addEventListener("storage", syncAuth);
    window.addEventListener("breadgo-auth-changed", syncAuth);
    window.addEventListener("breadgo-notifications-changed", syncAuth);
    return () => {
      window.removeEventListener("storage", syncAuth);
      window.removeEventListener("breadgo-auth-changed", syncAuth);
      window.removeEventListener("breadgo-notifications-changed", syncAuth);
    };
  }, []);

  function logout() {
    clearToken();
    setLoggedIn(false);
    setUserEmail(null);
    setUserRole(null);
    setUnreadCount(0);
    setWeeklyReportUnreadCount(0);
    setMenuOpen(false);
    router.replace("/");
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
            <span className="nav-user-email" title={userEmail || "로그인됨"}>
              {userEmail || "로그인됨"}
            </span>
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
