"use client";

import { useEffect, useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import { formatMoney } from "@/lib/format";
import { deliveryStatusLabel, type Payment, type Reservation, type ReservationHistory } from "@/lib/types";

function fulfillmentMethodLabel(value: string) {
  const labels: Record<string, string> = {
    PICKUP: "매장 직접 픽업",
    QUICK_DELIVERY: "퀵배달 요청",
    PARCEL_DELIVERY: "택배 배송",
  };
  return labels[value] || value;
}

function historyEventLabel(value: string) {
  const labels: Record<string, string> = {
    RESERVATION_CREATED: "예약 생성",
    PAYMENT_COMPLETED: "결제 완료",
    PICKUP_CONFIRMED: "픽업 완료",
    DELIVERY_STATUS_CHANGED: "배송 상태 변경",
    RESERVATION_CANCELLED: "예약 취소",
    MOCK_REFUND_PROCESSED: "Mock 환불 처리",
    SETTLEMENT_STATUS_CHANGED: "정산 상태 변경",
    RESERVATION_STATUS_CHANGED: "예약 상태 변경",
  };
  return labels[value] || value;
}

function reservationGuidance(status: string, fulfillmentMethod: string) {
  if (fulfillmentMethod === "QUICK_DELIVERY") {
    return "퀵배달 요청 정보가 매장에 전달되었습니다.";
  }
  if (fulfillmentMethod === "PARCEL_DELIVERY") {
    return "택배 배송 요청 정보가 매장에 전달되었습니다.";
  }

  switch (status) {
    case "CONFIRMED":
    case "PENDING":
      return "매장에서 픽업 코드를 보여주세요.";
    case "PICKED_UP":
      return "픽업이 완료되었습니다.";
    case "CANCELLED":
      return "취소된 예약입니다.";
    case "EXPIRED":
      return "만료된 예약입니다.";
    default:
      return "예약 상태를 확인해 주세요.";
  }
}

export default function MyReservationsPage() {
  const guard = useRoleGuard("CUSTOMER");
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [paymentMethod, setPaymentMethod] = useState("MOCK_CARD");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [payingReservationId, setPayingReservationId] = useState<string | null>(null);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [historyByReservation, setHistoryByReservation] = useState<Record<string, ReservationHistory[]>>({});
  const [expandedHistoryId, setExpandedHistoryId] = useState<string | null>(null);
  const [historyLoadingId, setHistoryLoadingId] = useState<string | null>(null);

  useEffect(() => {
    if (guard.allowed) {
      void loadReservations();
    }
  }, [guard.allowed]);

  async function loadReservations() {
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const [data, paymentData] = await Promise.all([
        apiFetch<Reservation[]>("/api/v1/reservations/me", { cache: "no-store" }, true),
        apiFetch<Payment[]>("/api/v1/payments/me", { cache: "no-store" }, true),
      ]);
      setReservations(data);
      setPayments(paymentData);
      setMessage(data.length > 0 ? `${data.length}개 예약을 불러왔습니다.` : "");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  function paymentMethodLabel(value: string) {
    switch (value) {
      case "MOCK_KAKAO_PAY":
        return "카카오페이 모의결제";
      case "MOCK_NAVER_PAY":
        return "네이버페이 모의결제";
      case "MOCK_CARD":
      default:
        return "카드 모의결제";
    }
  }

  function paymentForReservation(reservationId: string) {
    return payments.find((item) => item.reservation_id === reservationId);
  }

  function isUnpaidReservation(reservation: Reservation, payment: Payment | undefined) {
    const paymentStatus = reservation.payment_status || payment?.status || "";
    return !["PAID", "CANCELLED", "REFUNDED"].includes(paymentStatus);
  }

  async function payReservation(reservation: Reservation) {
    setMessage("");
    setIsError(false);
    setPayingReservationId(reservation.id);

    try {
      const existingPayment = paymentForReservation(reservation.id);
      const readyPayment =
        existingPayment?.status === "READY"
          ? existingPayment
          : await apiFetch<Payment>(
              "/api/v1/payments/mock/ready",
              {
                method: "POST",
                body: JSON.stringify({
                  reservation_id: reservation.id,
                  method: paymentMethod,
                }),
              },
              true,
            );
      const paid = await apiFetch<Payment>(
        "/api/v1/payments/mock/confirm",
        {
          method: "POST",
          body: JSON.stringify({ payment_id: readyPayment.id }),
        },
        true,
      );
      setPayments((current) => [paid, ...current.filter((item) => item.id !== paid.id)]);
      setReservations((current) =>
        current.map((item) => (item.id === reservation.id ? { ...item, payment_status: paid.status } : item)),
      );
      setMessage(`${paymentMethodLabel(paid.method)}가 완료되었습니다. 내 결제 화면에서도 확인할 수 있습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setPayingReservationId(null);
    }
  }

  function canCancelReservation(reservation: Reservation, paymentStatus: string) {
    return (
      reservation.status === "CONFIRMED" &&
      paymentStatus === "PAID" &&
      reservation.delivery_status !== "SENT" &&
      reservation.delivery_status !== "DELIVERED"
    );
  }

  async function cancelReservation(reservation: Reservation) {
    const confirmed = window.confirm(
      "예약을 취소하시겠습니까? MVP에서는 실제 카드 환불이 아닌 Mock 환불 처리입니다.",
    );
    if (!confirmed) {
      return;
    }

    setMessage("");
    setIsError(false);
    setCancellingId(reservation.id);

    try {
      const updated = await apiFetch<Reservation>(
        `/api/v1/reservations/${reservation.id}/cancel`,
        { method: "POST" },
        true,
      );
      const paymentData = await apiFetch<Payment[]>("/api/v1/payments/me", {}, true);
      setReservations((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setPayments(paymentData);
      setMessage("예약이 취소되었습니다. 현재는 실제 PG 환불이 아닌 MVP용 Mock 환불 상태입니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setCancellingId(null);
    }
  }

  async function toggleHistory(reservationId: string) {
    if (expandedHistoryId === reservationId) {
      setExpandedHistoryId(null);
      return;
    }

    setExpandedHistoryId(reservationId);
    if (historyByReservation[reservationId]) {
      return;
    }

    setHistoryLoadingId(reservationId);
    try {
      const history = await apiFetch<ReservationHistory[]>(
        `/api/v1/reservations/${reservationId}/history`,
        {},
        true,
      );
      setHistoryByReservation((current) => ({ ...current, [reservationId]: history }));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setHistoryLoadingId(null);
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
        title="내 예약"
        description="예약 상태, 결제 상태, 픽업코드를 한눈에 확인합니다."
        actions={
          <button type="button" onClick={loadReservations}>
            {loading ? "불러오는 중" : "새로고침"}
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      <div className="list">
        {reservations.length === 0 && !isError && (
          <EmptyState
            title="예약 내역이 없습니다."
            description="상품을 둘러보고 마감 할인 상품을 예약해 보세요."
          />
        )}
        {reservations.map((reservation) => {
          const payment = payments.find((item) => item.reservation_id === reservation.id);
          const paymentStatus = reservation.payment_status || payment?.status || "없음";
          return (
            <article className="item" key={reservation.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">예약 상품</p>
                  <h3>{reservation.product_name || "마감 할인 상품"}</h3>
                  <p>{reservation.store_name || "매장 정보 없음"}</p>
                </div>
                <StatusBadge status={reservation.status} />
              </div>
              {reservation.fulfillment_method === "PICKUP" && (
                <div className="pickup-code-block">
                  <span>픽업 코드</span>
                  <p className="pickup-code">{reservation.pickup_code}</p>
                </div>
              )}
              <p className="guidance-text">
                {reservationGuidance(reservation.status, reservation.fulfillment_method)}
              </p>
              <div className="meta">
                <span>
                  수령 방법 <strong>{fulfillmentMethodLabel(reservation.fulfillment_method)}</strong>
                </span>
                <span>
                  예약 상태 <StatusBadge status={reservation.status} />
                </span>
                <span>
                  결제 상태 {paymentStatus === "없음" ? "없음" : <StatusBadge status={paymentStatus} />}
                </span>
                <span>
                  상품 금액 <strong>{formatMoney(reservation.product_amount)}</strong>
                </span>
                <span>
                  배송비 <strong>{formatMoney(reservation.delivery_fee)}</strong>
                </span>
                <span>
                  총 고객 결제금액 <strong>{formatMoney(reservation.total_price)}</strong>
                </span>
                <span>수량 {reservation.quantity}</span>
              </div>
              {reservation.fulfillment_method !== "PICKUP" && (
                <div className="detail-grid">
                  <div>
                    <span>배송 상태</span>
                    <strong>{deliveryStatusLabel(reservation.delivery_status)}</strong>
                  </div>
                  <div>
                    <span>받는 사람</span>
                    <strong>{reservation.recipient_name || "-"}</strong>
                  </div>
                  <div>
                    <span>받는 사람 연락처</span>
                    <strong>{reservation.recipient_phone || "-"}</strong>
                  </div>
                  <div>
                    <span>주소</span>
                    <strong>{reservation.delivery_address || "-"}</strong>
                  </div>
                  <div>
                    <span>배송 요청사항</span>
                    <strong>{reservation.delivery_request_memo || "-"}</strong>
                  </div>
                </div>
              )}
              <div className="meta">
                <span>픽업 마감 {new Date(reservation.pickup_deadline).toLocaleString()}</span>
                <span>예약일 {new Date(reservation.created_at).toLocaleString()}</span>
              </div>
              <div className="actions">
                {isUnpaidReservation(reservation, payment) && (
                  <>
                    <label className="compact-action-field">
                      Mock 결제 수단
                      <select value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value)}>
                        <option value="MOCK_CARD">카드 모의결제</option>
                        <option value="MOCK_KAKAO_PAY">카카오페이 모의결제</option>
                        <option value="MOCK_NAVER_PAY">네이버페이 모의결제</option>
                      </select>
                    </label>
                    <button
                      type="button"
                      onClick={() => payReservation(reservation)}
                      disabled={payingReservationId === reservation.id}
                    >
                      {payingReservationId === reservation.id ? "결제 처리 중" : "결제하기"}
                    </button>
                  </>
                )}
                <button type="button" className="secondary" onClick={() => toggleHistory(reservation.id)}>
                  {expandedHistoryId === reservation.id ? "상태 이력 닫기" : "상태 이력"}
                </button>
              </div>
              {expandedHistoryId === reservation.id && (
                <div className="timeline">
                  {historyLoadingId === reservation.id && <p className="field-help">상태 이력을 불러오는 중입니다.</p>}
                  {(historyByReservation[reservation.id] || []).map((event) => (
                    <div className="timeline-item" key={event.id}>
                      <strong>{historyEventLabel(event.event_type)}</strong>
                      <span>{event.message}</span>
                      <small>
                        {[event.actor_email || event.actor_role, event.from_status && event.to_status
                          ? `${event.from_status} → ${event.to_status}`
                          : null, new Date(event.created_at).toLocaleString()]
                          .filter(Boolean)
                          .join(" · ")}
                      </small>
                    </div>
                  ))}
                  {!historyLoadingId && (historyByReservation[reservation.id] || []).length === 0 && (
                    <p className="field-help">상태 이력이 없습니다.</p>
                  )}
                </div>
              )}
              {canCancelReservation(reservation, paymentStatus) && (
                <div className="actions">
                  <button
                    type="button"
                    className="danger"
                    onClick={() => cancelReservation(reservation)}
                    disabled={cancellingId === reservation.id}
                  >
                    {cancellingId === reservation.id ? "취소 처리 중" : "예약 취소"}
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
