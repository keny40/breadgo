"use client";

import { useState } from "react";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Payment } from "@/lib/types";

export default function MyPaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  async function loadPayments() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Payment[]>("/api/v1/payments/me", {}, true);
      setPayments(data);
      setMessage(`${data.length}개 결제를 불러왔습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <h1>내 결제</h1>
      <div className="actions">
        <button type="button" onClick={loadPayments}>
          결제 불러오기
        </button>
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      <div className="list">
        {payments.length === 0 && !isError && <div className="empty-state">결제 내역이 없습니다.</div>}
        {payments.map((payment) => (
          <article className="item" key={payment.id}>
            <h3>{payment.status}</h3>
            <div className="meta">
              <span>금액 {payment.amount}</span>
              <span>수단 {payment.method}</span>
              <span>예약 {payment.reservation_id}</span>
              <span>결제일 {payment.paid_at ? new Date(payment.paid_at).toLocaleString() : "-"}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
