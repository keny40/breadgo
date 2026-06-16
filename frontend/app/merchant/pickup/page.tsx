"use client";

import { FormEvent, useState } from "react";
import { PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { PickupConfirmResponse, Reservation } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

export default function MerchantPickupPage() {
  const [pickupCode, setPickupCode] = useState("");
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  async function findReservation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

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
      setMessage(friendlyErrorMessage(error));
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
      setMessage(`픽업 확정 완료. 상태: ${data.reservation.status}`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="픽업 확인"
        description="고객이 제시한 6자리 픽업코드를 조회한 뒤 픽업을 확정합니다."
      />
      <form className="panel form-grid" onSubmit={findReservation}>
        <label>
          픽업코드
          <input
            value={pickupCode}
            onChange={(event) => setPickupCode(event.target.value)}
            minLength={6}
            maxLength={6}
            required
          />
        </label>
        <div className="actions">
          <button type="submit">예약 조회</button>
          <button type="button" className="secondary" onClick={confirmPickup}>
            픽업 확정
          </button>
        </div>
      </form>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {reservation && (
        <article className="item">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">조회된 픽업코드</p>
              <p className="pickup-code">{reservation.pickup_code}</p>
            </div>
            <StatusBadge status={reservation.status} />
          </div>
          <div className="meta">
            <span>예약 {reservation.id}</span>
            <span>상품 {reservation.product_id}</span>
            <span>매장 {reservation.store_id}</span>
            <span>수량 {reservation.quantity}</span>
            <span>총액 {formatMoney(reservation.total_price)}</span>
          </div>
          <div className="meta">
            <span>예약 시간 {new Date(reservation.reserved_at).toLocaleString()}</span>
            <span>픽업 마감 {new Date(reservation.pickup_deadline).toLocaleString()}</span>
          </div>
        </article>
      )}
    </section>
  );
}
