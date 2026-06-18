"use client";

import { useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { Payment } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function paymentMethodLabel(value: string) {
  switch (value) {
    case "MOCK_CARD":
      return "카드 모의결제";
    case "MOCK_KAKAO_PAY":
      return "카카오페이 모의결제";
    case "MOCK_NAVER_PAY":
      return "네이버페이 모의결제";
    default:
      return value;
  }
}

function fulfillmentMethodLabel(value: string | null) {
  const labels: Record<string, string> = {
    PICKUP: "매장 직접 픽업",
    QUICK_DELIVERY: "퀵배달 요청",
    PARCEL_DELIVERY: "택배 배송",
  };
  return value ? labels[value] || value : "-";
}

export default function MyPaymentsPage() {
  const guard = useRoleGuard("CUSTOMER");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function loadPayments() {
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await apiFetch<Payment[]>("/api/v1/payments/me", {}, true);
      setPayments(data);
      setMessage(data.length > 0 ? `${data.length}개 결제를 불러왔습니다.` : "");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
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
        title="내 결제"
        description="Mock 결제 수단, 금액, 결제 상태를 확인합니다."
        actions={
          <button type="button" onClick={loadPayments}>
            {loading ? "불러오는 중" : "새로고침"}
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
              <div>
                <p className="eyebrow">결제 상품</p>
                <h3>{payment.product_name || "마감 할인 상품"}</h3>
                <p>{payment.store_name || "매장 정보 없음"}</p>
              </div>
              <StatusBadge status={payment.status} />
            </div>
            <div className="detail-grid">
              <div>
                <span>결제 금액</span>
                <strong>{formatMoney(payment.amount)}</strong>
              </div>
              <div>
                <span>결제 수단</span>
                <strong>{paymentMethodLabel(payment.method)}</strong>
              </div>
              <div>
                <span>결제 상태</span>
                <strong>
                  <StatusBadge status={payment.status} />
                </strong>
              </div>
              <div>
                <span>수령 방법</span>
                <strong>{fulfillmentMethodLabel(payment.fulfillment_method)}</strong>
              </div>
              <div>
                <span>배송비</span>
                <strong>{payment.delivery_fee ? formatMoney(payment.delivery_fee) : "0원"}</strong>
              </div>
              <div>
                <span>예약 상태</span>
                <strong>
                  {payment.reservation_status ? <StatusBadge status={payment.reservation_status} /> : "-"}
                </strong>
              </div>
            </div>
            <div className="meta">
              {payment.fulfillment_method === "PICKUP" && payment.pickup_code && <span>픽업코드 {payment.pickup_code}</span>}
              {payment.delivery_status && <span>배송 상태 {payment.delivery_status}</span>}
              <span>생성일 {new Date(payment.created_at).toLocaleString()}</span>
              <span>결제일 {payment.paid_at ? new Date(payment.paid_at).toLocaleString() : "-"}</span>
              {payment.cancelled_at && <span>취소일 {new Date(payment.cancelled_at).toLocaleString()}</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
