"use client";

import { useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Payment } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

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
      <PageHeader
        title="내 결제"
        description="Mock 결제 수단, 금액, 결제 상태를 확인합니다."
        actions={
          <button type="button" onClick={loadPayments}>
            결제 불러오기
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      <div className="list">
        {payments.length === 0 && !isError && (
          <EmptyState title="결제 내역이 없습니다." description="상품 예약 후 Mock 결제를 진행하면 이곳에 표시됩니다." />
        )}
        {payments.map((payment) => (
          <article className="item" key={payment.id}>
            <div className="card-title-row">
              <h3>{formatMoney(payment.amount)}</h3>
              <StatusBadge status={payment.status} />
            </div>
            <div className="meta">
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
