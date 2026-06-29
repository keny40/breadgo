"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import {
  deliveryStatusLabel,
  deliveryStatuses,
  type PickupConfirmResponse,
  type Reservation,
} from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDateTime(value: string) {
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

function pickupErrorMessage(error: unknown) {
  const message = error instanceof Error ? error.message : "";
  const lower = message.toLowerCase();

  if (lower.includes("pickup code") || lower.includes("not found")) {
    return "픽업 코드를 찾을 수 없습니다.";
  }
  if (lower.includes("current status")) {
    return "취소/만료/픽업 완료된 예약은 픽업 확정할 수 없습니다.";
  }
  return friendlyErrorMessage(error);
}

function isPickupBlocked(status: string) {
  return ["PICKED_UP", "CANCELLED", "EXPIRED"].includes(status);
}

function isPickupFulfillment(reservation: Reservation) {
  return reservation.fulfillment_method === "PICKUP";
}

export default function MerchantPickupPage() {
  const guard = useRoleGuard("MERCHANT");
  const [pickupCode, setPickupCode] = useState("");
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [updatingDeliveryStatus, setUpdatingDeliveryStatus] = useState(false);

  async function findReservation(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await apiFetch<Reservation>(
        `/api/v1/reservations/pickup/${pickupCode}`,
        {},
        true,
      );
      setReservation(data);
      setMessage("예약을 찾았습니다.");
    } catch (error) {
      setReservation(null);
      setIsError(true);
      setMessage(pickupErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function confirmPickup() {
    setMessage("");
    setIsError(false);

    if (!reservation) {
      setIsError(true);
      setMessage("먼저 픽업코드로 예약을 조회하세요.");
      return;
    }

    if (reservation.status === "PICKED_UP") {
      setIsError(true);
      setMessage("이미 픽업 완료된 예약입니다.");
      return;
    }

    if (["CANCELLED", "EXPIRED"].includes(reservation.status)) {
      setIsError(true);
      setMessage("취소/만료된 예약은 픽업 확정할 수 없습니다.");
      return;
    }

    setConfirming(true);
    try {
      const data = await apiFetch<PickupConfirmResponse>(
        "/api/v1/reservations/pickup/confirm",
        {
          method: "POST",
          body: JSON.stringify({ pickup_code: pickupCode }),
        },
        true,
      );
      setReservation(data.reservation);
      setMessage("픽업 확정이 완료되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(pickupErrorMessage(error));
    } finally {
      setConfirming(false);
    }
  }

  async function updateDeliveryStatus(nextStatus: string) {
    if (!reservation) {
      return;
    }

    setMessage("");
    setIsError(false);
    setUpdatingDeliveryStatus(true);

    try {
      const updated = await apiFetch<Reservation>(
        `/api/v1/reservations/${reservation.id}/delivery-status`,
        {
          method: "PATCH",
          body: JSON.stringify({ delivery_status: nextStatus }),
        },
        true,
      );
      setReservation(updated);
      setMessage(`배송 상태가 ${deliveryStatusLabel(nextStatus)}(으)로 변경되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setUpdatingDeliveryStatus(false);
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
        title="픽업 확인"
        description="고객이 제시한 6자리 픽업 코드를 조회하고 예약 상태를 확인한 뒤 픽업을 확정합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/merchant/orders">
              주문 관리
            </Link>
            <Link className="button-link secondary" href="/merchant/products">
              상품/재고 관리
            </Link>
          </>
        }
      />
      <p className="message">
        픽업 확정은 BreadGo 내부 예약 상태와 재고 이력에 반영됩니다. 배송 요청 상태는 실제 배송 provider 없이 점주가 수동으로 관리합니다.
      </p>

      <form className="panel form-grid pickup-search-panel" onSubmit={findReservation}>
        <label>
          픽업 코드
          <input
            value={pickupCode}
            onChange={(event) => setPickupCode(event.target.value)}
            minLength={6}
            maxLength={6}
            placeholder="예) 363790"
            inputMode="numeric"
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "조회 중" : "예약 조회"}
        </button>
      </form>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!reservation && !isError && (
        <EmptyState
          title="조회된 예약이 없습니다."
          description="고객의 픽업 코드를 입력한 뒤 예약 조회를 눌러주세요."
        />
      )}

      {reservation && (
        <article className="item pickup-detail-card">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">
                {isPickupFulfillment(reservation) ? "픽업 코드" : "배송 요청 예약 코드"}
              </p>
              {isPickupFulfillment(reservation) ? (
                <p className="pickup-code">{reservation.pickup_code}</p>
              ) : (
                <h2>{reservation.pickup_code}</h2>
              )}
            </div>
            <StatusBadge status={reservation.status} />
          </div>

          <div className="summary-grid">
            <PickupInfo label="상품" value={reservation.product_name || "상품 정보 없음"} />
            <PickupInfo label="매장" value={reservation.store_name || "매장 정보 없음"} />
            <PickupInfo
              label="고객"
              value={reservation.customer_name || reservation.customer_email || "고객 정보 없음"}
              helper={reservation.customer_email || undefined}
            />
            <PickupInfo label="수량" value={`${reservation.quantity}개`} />
            <PickupInfo label="수령 방법" value={fulfillmentMethodLabel(reservation.fulfillment_method)} />
            <PickupInfo label="상품 금액" value={formatMoney(reservation.product_amount)} />
            <PickupInfo label="배송비" value={formatMoney(reservation.delivery_fee)} />
            <PickupInfo label="총 고객 결제금액" value={formatMoney(reservation.total_price)} />
            <PickupInfo
              label="결제 상태"
              value={reservation.payment_status || "결제 정보 없음"}
              badge={reservation.payment_status || undefined}
            />
            <PickupInfo label="픽업 마감" value={formatDateTime(reservation.pickup_deadline)} />
            <PickupInfo label="예약 생성" value={formatDateTime(reservation.created_at)} />
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

          {isPickupFulfillment(reservation) ? (
            <div className="actions">
              <button
                type="button"
                onClick={confirmPickup}
                disabled={confirming || isPickupBlocked(reservation.status)}
              >
                {confirming ? "확정 중" : "픽업 확정"}
              </button>
              {isPickupBlocked(reservation.status) && (
                <span className="field-help">현재 상태에서는 픽업 확정을 진행할 수 없습니다.</span>
              )}
            </div>
          ) : (
            <div className="payment-box">
              <p className="message">
                현재는 실제 배송 연동이 아닌 MVP용 배송 상태 관리입니다. 배송 상태는 점주가 수동으로 변경합니다.
              </p>
              <label>
                배송 상태
                <select
                  value={reservation.delivery_status}
                  onChange={(event) => updateDeliveryStatus(event.target.value)}
                  disabled={updatingDeliveryStatus}
                >
                  {deliveryStatuses.map((status) => (
                    <option key={status} value={status}>
                      {deliveryStatusLabel(status)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}
        </article>
      )}
    </section>
  );
}

function PickupInfo({
  label,
  value,
  helper,
  badge,
}: {
  label: string;
  value: string;
  helper?: string;
  badge?: string;
}) {
  return (
    <div className="summary-card">
      <span>{label}</span>
      {badge ? <StatusBadge status={badge} /> : <strong>{value}</strong>}
      {helper && <small>{helper}</small>}
    </div>
  );
}
