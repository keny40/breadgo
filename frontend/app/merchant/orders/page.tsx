"use client";

import { useEffect, useMemo, useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import {
  deliveryStatusLabel,
  deliveryStatuses,
  type PickupConfirmResponse,
  type Reservation,
} from "@/lib/types";

const orderFilters = [
  "전체",
  "오늘 예약",
  "픽업",
  "퀵배달",
  "택배",
  "결제완료",
  "픽업완료",
  "배송 요청",
  "배송 완료",
  "취소",
];

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function fulfillmentMethodLabel(value: string) {
  const labels: Record<string, string> = {
    PICKUP: "매장 직접 픽업",
    QUICK_DELIVERY: "퀵배달 요청",
    PARCEL_DELIVERY: "택배 배송",
  };
  return labels[value] || value;
}

function matchesFilter(reservation: Reservation, filter: string) {
  const today = new Date().toDateString();
  switch (filter) {
    case "오늘 예약":
      return new Date(reservation.created_at).toDateString() === today;
    case "픽업":
      return reservation.fulfillment_method === "PICKUP";
    case "퀵배달":
      return reservation.fulfillment_method === "QUICK_DELIVERY";
    case "택배":
      return reservation.fulfillment_method === "PARCEL_DELIVERY";
    case "결제완료":
      return reservation.payment_status === "PAID";
    case "픽업완료":
      return reservation.status === "PICKED_UP";
    case "배송 요청":
      return reservation.delivery_status === "REQUESTED";
    case "배송 완료":
      return reservation.delivery_status === "DELIVERED";
    case "취소":
      return reservation.status === "CANCELLED" || reservation.delivery_status === "CANCELLED";
    default:
      return true;
  }
}

function canConfirmPickup(reservation: Reservation) {
  return (
    reservation.fulfillment_method === "PICKUP" &&
    reservation.status === "CONFIRMED" &&
    reservation.payment_status === "PAID"
  );
}

export default function MerchantOrdersPage() {
  const guard = useRoleGuard("MERCHANT");
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [filter, setFilter] = useState("전체");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadOrders();
  }, [guard.allowed]);

  const filteredReservations = useMemo(
    () => reservations.filter((reservation) => matchesFilter(reservation, filter)),
    [filter, reservations],
  );

  async function loadOrders() {
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await apiFetch<Reservation[]>("/api/v1/reservations/merchant", {}, true);
      setReservations(data);
      setMessage(data.length > 0 ? `${data.length}개 주문을 불러왔습니다.` : "");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function confirmPickup(reservation: Reservation) {
    setMessage("");
    setIsError(false);
    setUpdatingId(reservation.id);

    try {
      const data = await apiFetch<PickupConfirmResponse>(
        "/api/v1/reservations/pickup/confirm",
        {
          method: "POST",
          body: JSON.stringify({ pickup_code: reservation.pickup_code }),
        },
        true,
      );
      setReservations((current) =>
        current.map((item) => (item.id === reservation.id ? data.reservation : item)),
      );
      setMessage("픽업 확정이 완료되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setUpdatingId(null);
    }
  }

  async function updateDeliveryStatus(reservation: Reservation, nextStatus: string) {
    setMessage("");
    setIsError(false);
    setUpdatingId(reservation.id);

    try {
      const updated = await apiFetch<Reservation>(
        `/api/v1/reservations/${reservation.id}/delivery-status`,
        {
          method: "PATCH",
          body: JSON.stringify({ delivery_status: nextStatus }),
        },
        true,
      );
      setReservations((current) =>
        current.map((item) => (item.id === reservation.id ? updated : item)),
      );
      setMessage(`배송 상태가 ${deliveryStatusLabel(nextStatus)}(으)로 변경되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setUpdatingId(null);
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
        title="주문 관리"
        description="픽업 주문, 퀵배달 요청, 택배 배송 요청을 한 화면에서 확인하고 처리합니다."
        actions={
          <button type="button" onClick={loadOrders} disabled={loading}>
            {loading ? "불러오는 중" : "주문 새로고침"}
          </button>
        }
      />
      <p className="message">
        배송 상태는 점주가 수동으로 변경합니다. 현재는 실제 배송 연동이 아닌 MVP용 주문 관리입니다.
      </p>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="chip-row">
        {orderFilters.map((item) => (
          <button
            type="button"
            className={`chip ${filter === item ? "active" : ""}`}
            key={item}
            onClick={() => setFilter(item)}
          >
            {item}
          </button>
        ))}
      </div>

      {filteredReservations.length === 0 ? (
        <EmptyState title="표시할 주문이 없습니다." description="필터를 변경하거나 새로고침해 주세요." />
      ) : (
        <div className="list">
          {filteredReservations.map((reservation) => (
            <article className="item" key={reservation.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">주문</p>
                  <h3>{reservation.product_name || "마감 할인 상품"}</h3>
                  <p>{reservation.store_name || "매장 정보 없음"}</p>
                </div>
                <div className="actions">
                  <StatusBadge status={reservation.status} />
                  {reservation.payment_status && <StatusBadge status={reservation.payment_status} />}
                </div>
              </div>

              <div className="detail-grid">
                <OrderInfo label="고객" value={reservation.customer_name || reservation.customer_email || "-"} />
                <OrderInfo label="수량" value={`${reservation.quantity}개`} />
                <OrderInfo label="상품 금액" value={formatMoney(reservation.product_amount)} />
                <OrderInfo label="배송비" value={formatMoney(reservation.delivery_fee)} />
                <OrderInfo label="총 고객 결제금액" value={formatMoney(reservation.total_price)} />
                <OrderInfo label="수령 방법" value={fulfillmentMethodLabel(reservation.fulfillment_method)} />
                <OrderInfo label="예약 상태" value={reservation.status} badge />
                <OrderInfo label="결제 상태" value={reservation.payment_status || "미결제"} badge={Boolean(reservation.payment_status)} />
                <OrderInfo label="배송 상태" value={deliveryStatusLabel(reservation.delivery_status)} />
                <OrderInfo label="예약일" value={formatDate(reservation.created_at)} />
                <OrderInfo label="픽업 마감" value={formatDate(reservation.pickup_deadline)} />
              </div>

              {reservation.fulfillment_method === "PICKUP" ? (
                <div className="pickup-code-block">
                  <span>픽업 코드</span>
                  <p className="pickup-code">{reservation.pickup_code}</p>
                </div>
              ) : (
                <>
                  <div className="detail-grid">
                    <OrderInfo label="받는 사람" value={reservation.recipient_name || "-"} />
                    <OrderInfo label="연락처" value={reservation.recipient_phone || "-"} />
                    <OrderInfo label="주소" value={reservation.delivery_address || "-"} />
                    <OrderInfo label="배송 요청사항" value={reservation.delivery_request_memo || "-"} />
                  </div>
                  <label>
                    배송 상태
                    <select
                      value={reservation.delivery_status}
                      onChange={(event) => updateDeliveryStatus(reservation, event.target.value)}
                      disabled={updatingId === reservation.id}
                    >
                      {deliveryStatuses.map((status) => (
                        <option key={status} value={status}>
                          {deliveryStatusLabel(status)}
                        </option>
                      ))}
                    </select>
                  </label>
                </>
              )}

              {canConfirmPickup(reservation) && (
                <div className="actions">
                  <button
                    type="button"
                    onClick={() => confirmPickup(reservation)}
                    disabled={updatingId === reservation.id}
                  >
                    픽업 확정
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function OrderInfo({ label, value, badge }: { label: string; value: string; badge?: boolean }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{badge ? <StatusBadge status={value} /> : value}</strong>
    </div>
  );
}
