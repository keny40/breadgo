"use client";

import { useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Payment, Reservation } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

export default function MyReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  async function loadReservations() {
    setMessage("");
    setIsError(false);

    try {
      const [data, paymentData] = await Promise.all([
        apiFetch<Reservation[]>("/api/v1/reservations/me", {}, true),
        apiFetch<Payment[]>("/api/v1/payments/me", {}, true),
      ]);
      setReservations(data);
      setPayments(paymentData);
      setMessage(`${data.length}개 예약을 불러왔습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="내 예약"
        description="예약 상태, 결제 상태, 픽업코드를 한눈에 확인합니다."
        actions={
          <button type="button" onClick={loadReservations}>
            예약 불러오기
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      <div className="list">
        {reservations.length === 0 && !isError && (
          <EmptyState title="예약 내역이 없습니다." description="상품 보기에서 마감 할인 상품을 예약해 보세요." />
        )}
        {reservations.map((reservation) => {
          const payment = payments.find((item) => item.reservation_id === reservation.id);
          return (
            <article className="item" key={reservation.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">픽업코드</p>
                  <p className="pickup-code">{reservation.pickup_code}</p>
                </div>
                <StatusBadge status={reservation.status} />
              </div>
              <div className="meta">
                <span>
                  예약 상태 <StatusBadge status={reservation.status} />
                </span>
                <span>
                  결제 상태 {payment ? <StatusBadge status={payment.status} /> : "없음"}
                </span>
                <span>
                  총액 <strong>{formatMoney(reservation.total_price)}</strong>
                </span>
                <span>수량 {reservation.quantity}</span>
                <span>상품 {reservation.product_id}</span>
              </div>
              <div className="meta">
                <span>픽업 마감 {new Date(reservation.pickup_deadline).toLocaleString()}</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
