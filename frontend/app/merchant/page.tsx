"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { Merchant, MerchantMeResponse, Reservation, Store } from "@/lib/types";

type ReservationSummary = {
  todayConfirmed: number;
  pickedUp: number;
  cancelled: number;
};

export default function MerchantPage() {
  const guard = useRoleGuard("MERCHANT");
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [businessName, setBusinessName] = useState("");
  const [businessRegistrationNumber, setBusinessRegistrationNumber] = useState("");
  const [representativeName, setRepresentativeName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [summary, setSummary] = useState<ReservationSummary | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!guard.allowed) {
      return;
    }
    void loadMerchant();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [guard.allowed]);

  async function loadMerchant() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<MerchantMeResponse>("/api/v1/merchants/me", {}, true);
      setMerchant(data.merchant);
      await loadReservationSummary();
      setMessage("가맹점 정보를 불러왔습니다.");
    } catch (error) {
      setMerchant(null);
      setSummary(null);
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function loadReservationSummary() {
    const stores = await apiFetch<Store[]>("/api/v1/stores/me", {}, true);
    const reservationGroups = await Promise.all(
      stores.map((store) => apiFetch<Reservation[]>(`/api/v1/stores/${store.id}/reservations`, {}, true)),
    );
    const reservations = reservationGroups.flat();
    const todayKey = new Date().toDateString();

    setSummary({
      todayConfirmed: reservations.filter(
        (reservation) =>
          reservation.status === "CONFIRMED" && new Date(reservation.created_at).toDateString() === todayKey,
      ).length,
      pickedUp: reservations.filter((reservation) => reservation.status === "PICKED_UP").length,
      cancelled: reservations.filter((reservation) => reservation.status === "CANCELLED").length,
    });
  }

  async function registerMerchant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Merchant>(
        "/api/v1/merchants/register",
        {
          method: "POST",
          body: JSON.stringify({
            business_name: businessName,
            business_registration_number: businessRegistrationNumber,
            representative_name: representativeName,
            phone_number: phoneNumber,
          }),
        },
        true,
      );
      setMerchant(data);
      setMessage("가맹점 등록이 완료되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  return (
    <section className="section">
      <PageHeader
        title="가맹점 대시보드"
        description="가맹점 등록 상태와 기본 사업자 정보를 확인합니다. 데모에서는 픽업 확인, 상품 관리, BreadGo Pro 리포트 흐름을 이어서 시연합니다."
        actions={
          <>
            <button type="button" onClick={loadMerchant}>
              내 가맹점 정보 확인
            </button>
            <Link className="button-link secondary" href="/merchant/pickup">
              픽업 확인
            </Link>
            <Link className="button-link secondary" href="/merchant/pro">
              BreadGo Pro
            </Link>
          </>
        }
      />
      <p className="message">
        POS, 배송, 외부 알림은 실제 연동 전 단계입니다. 데모에서는 BreadGo 내부 데이터와 Mock 흐름으로 운영 동선을 확인합니다.
      </p>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {merchant ? (
        <>
          <article className="item">
            <div className="card-title-row">
              <h3>{merchant.business_name}</h3>
              <StatusBadge status={merchant.status} />
            </div>
            <div className="meta">
              <span>사업자번호 {merchant.business_registration_number}</span>
              <span>대표자 {merchant.representative_name}</span>
              <span>전화 {merchant.phone_number}</span>
            </div>
          </article>
          {summary && (
            <>
              <div className="summary-grid">
                <div className="summary-card">
                  <span>오늘 확정 예약</span>
                  <strong>{summary.todayConfirmed}</strong>
                </div>
                <div className="summary-card">
                  <span>픽업 완료</span>
                  <strong>{summary.pickedUp}</strong>
                </div>
                <div className="summary-card">
                  <span>취소 예약</span>
                  <strong>{summary.cancelled}</strong>
                </div>
              </div>

              <section className="panel">
                <div className="card-title-row">
                  <div>
                    <p className="eyebrow">Merchant Operations</p>
                    <h2>오늘 먼저 확인할 점주 운영 흐름</h2>
                    <p>
                      상품 재고를 등록하고, 예약/결제 상태를 확인한 뒤, 고객 픽업 코드를 입력해 수령을 확정합니다.
                      BreadGo Pro에서는 재고 이력과 Weekly Report 알림을 이어서 확인합니다.
                    </p>
                  </div>
                  <Link className="button-link secondary" href="/merchant/products">
                    상품/재고 관리
                  </Link>
                </div>
                <div className="account-grid">
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>1. 상품과 재고</h3>
                      <span className="badge success">Stock</span>
                    </div>
                    <p>오늘 판매할 마감 할인 상품을 등록하고 남은 재고와 판매 상태를 확인합니다.</p>
                    <Link href="/merchant/products">
                      <button type="button" className="secondary">상품 관리</button>
                    </Link>
                  </article>
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>2. 예약과 픽업</h3>
                      <span className="badge warning">Pickup</span>
                    </div>
                    <p>결제 완료 예약을 확인하고 고객이 제시한 픽업 코드로 수령을 확정합니다.</p>
                    <div className="actions">
                      <Link href="/merchant/orders">
                        <button type="button" className="secondary">주문 관리</button>
                      </Link>
                      <Link href="/merchant/pickup">
                        <button type="button" className="secondary">픽업 확인</button>
                      </Link>
                    </div>
                  </article>
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>3. Pro 운영 확인</h3>
                      <span className="badge muted">Mock</span>
                    </div>
                    <p>재고 이력, Weekly Report 알림, POS 준비 흐름을 확인합니다. 실제 POS/배송/외부 알림은 아직 연결하지 않습니다.</p>
                    <Link href="/merchant/pro">
                      <button type="button" className="secondary">BreadGo Pro</button>
                    </Link>
                  </article>
                </div>
              </section>
            </>
          )}
        </>
      ) : (
        <form className="panel form-grid" onSubmit={registerMerchant}>
          <h2>가맹점 등록</h2>
          <p className="message">매장과 상품을 등록하려면 먼저 가맹점 프로필을 생성해야 합니다.</p>
          <label>
            상호명
            <input value={businessName} onChange={(event) => setBusinessName(event.target.value)} required />
          </label>
          <label>
            사업자등록번호
            <input
              value={businessRegistrationNumber}
              onChange={(event) => setBusinessRegistrationNumber(event.target.value)}
              required
            />
          </label>
          <label>
            대표자명
            <input
              value={representativeName}
              onChange={(event) => setRepresentativeName(event.target.value)}
              required
            />
          </label>
          <label>
            연락처
            <input value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} required />
          </label>
          <button type="submit">가맹점 등록</button>
        </form>
      )}
    </section>
  );
}
