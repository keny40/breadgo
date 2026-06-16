"use client";

import { useState } from "react";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Payment, Reservation } from "@/lib/types";

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
      <h1>내 예약</h1>
      <div className="actions">
        <button type="button" onClick={loadReservations}>
          예약 불러오기
        </button>
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      <div className="list">
        {reservations.length === 0 && !isError && <div className="empty-state">예약 내역이 없습니다.</div>}
        {reservations.map((reservation) => {
          const payment = payments.find((item) => item.reservation_id === reservation.id);
          return (
            <article className="item" key={reservation.id}>
              <h3>{reservation.pickup_code}</h3>
              <div className="meta">
                <span>상태 {reservation.status}</span>
                <span>결제 {payment ? payment.status : "없음"}</span>
                <span>총액 {reservation.total_price}</span>
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
