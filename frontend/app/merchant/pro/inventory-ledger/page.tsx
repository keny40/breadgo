"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { ProductInventoryEvent } from "@/lib/types";

const eventLabels: Record<string, string> = {
  MANUAL_CREATE: "수동 생성",
  MANUAL_UPDATE: "수동 수정",
  CSV_IMPORT_CREATE: "CSV 생성",
  CSV_IMPORT_UPDATE: "CSV 업데이트",
  POS_SYNC_CREATE: "POS 생성",
  POS_SYNC_UPDATE: "POS 업데이트",
  RECOMMENDATION_DRAFT_CREATE: "추천 초안 생성",
  RESERVATION_CREATED: "예약 생성",
  RESERVATION_CANCELLED: "예약 취소",
  PICKUP_COMPLETED: "픽업 완료",
  ADJUSTMENT: "재고 조정",
};

const sourceLabels: Record<string, string> = {
  MANUAL: "수동",
  CSV: "CSV",
  POS: "POS",
  RECOMMENDATION: "추천",
  RESERVATION: "예약",
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatQuantity(value: number | null) {
  return value === null ? "-" : `${value}개`;
}

function deltaLabel(value: number | null) {
  if (value === null) return "-";
  if (value > 0) return `+${value}개`;
  return `${value}개`;
}

function deltaTone(value: number | null): "success" | "warning" | "danger" | "muted" {
  if (value === null || value === 0) return "muted";
  return value > 0 ? "success" : "danger";
}

export default function MerchantProInventoryLedgerPage() {
  const guard = useRoleGuard("MERCHANT");
  const [events, setEvents] = useState<ProductInventoryEvent[]>([]);
  const [eventType, setEventType] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadEvents = useCallback(async (overrides?: { eventType?: string; sourceType?: string }) => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const params = new URLSearchParams();
      const nextEventType = overrides?.eventType ?? eventType;
      const nextSourceType = overrides?.sourceType ?? sourceType;
      if (nextEventType) params.set("event_type", nextEventType);
      if (nextSourceType) params.set("source_type", nextSourceType);
      params.set("limit", "50");
      const query = params.toString();
      const data = await apiFetch<ProductInventoryEvent[]>(
        `/api/v1/merchant/pro/inventory-events${query ? `?${query}` : ""}`,
        {},
        true,
      );
      setEvents(data);
      setMessage("재고 변경 이력을 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [eventType, sourceType]);

  useEffect(() => {
    if (!guard.allowed) return;
    void Promise.resolve().then(() => loadEvents());
  }, [guard.allowed, loadEvents]);

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  const increaseCount = events.filter((event) => (event.quantity_delta || 0) > 0).length;
  const decreaseCount = events.filter((event) => (event.quantity_delta || 0) < 0).length;

  return (
    <section className="section">
      <PageHeader
        title="재고 변경 이력"
        description="CSV, POS, 추천, 예약, 수동 수정으로 인한 재고 변동 원인을 추적합니다."
        actions={
          <>
            <button type="button" onClick={() => void loadEvents()} disabled={loading}>
              {loading ? "불러오는 중" : "이력 새로고침"}
            </button>
            <Link className="button-link secondary" href="/merchant/pro/inventory-alerts">
              재고 이상 알림 보기
            </Link>
          </>
        }
      />

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">Inventory Ledger</p>
          <h2>재고 변경 원인을 추적합니다</h2>
          <p>CSV/POS/예약/추천으로 인한 재고 변동을 한눈에 확인해 점주 운영 판단의 근거로 사용합니다.</p>
        </div>
        <div className="pro-score">
          <span>최근 이력</span>
          <strong>{events.length}건</strong>
          <small>최근 50건 기준</small>
        </div>
      </div>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="summary-grid">
        <StatCard label="전체 이벤트" value={`${events.length}건`} />
        <StatCard label="재고 증가" value={`${increaseCount}건`} />
        <StatCard label="재고 감소" value={`${decreaseCount}건`} />
        <StatCard label="추적 범위" value="최근 50건" helper="이번 Phase 이후 이벤트" />
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">필터</p>
            <h2>출처와 변경 유형으로 확인</h2>
          </div>
        </div>
        <div className="form-grid">
          <label>
            변경 유형
            <select value={eventType} onChange={(event) => setEventType(event.target.value)}>
              <option value="">전체</option>
              {Object.entries(eventLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            출처
            <select value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
              <option value="">전체</option>
              {Object.entries(sourceLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="actions">
          <button type="button" onClick={() => void loadEvents()} disabled={loading}>
            필터 적용
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setEventType("");
              setSourceType("");
              void loadEvents({ eventType: "", sourceType: "" });
            }}
          >
            전체 보기
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">최근 재고 변경</p>
            <h2>Inventory Ledger</h2>
          </div>
          <Badge tone="muted">개인정보 저장 없음</Badge>
        </div>
        {events.length === 0 ? (
          <EmptyState
            title="재고 변경 이력이 없습니다."
            description="상품 등록, CSV import, POS sync, 예약 생성/취소가 발생하면 이력이 표시됩니다."
          />
        ) : (
          <div className="responsive-table">
            <table>
              <thead>
                <tr>
                  <th>발생 시각</th>
                  <th>상품</th>
                  <th>매장</th>
                  <th>변경 유형</th>
                  <th>이전</th>
                  <th>이후</th>
                  <th>증감</th>
                  <th>출처</th>
                  <th>메모</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id}>
                    <td>{formatDateTime(event.created_at)}</td>
                    <td>{event.product_name || "-"}</td>
                    <td>{event.store_name || "-"}</td>
                    <td>{eventLabels[event.event_type] || event.event_type}</td>
                    <td>{formatQuantity(event.quantity_before)}</td>
                    <td>{formatQuantity(event.quantity_after)}</td>
                    <td>
                      <Badge tone={deltaTone(event.quantity_delta)}>{deltaLabel(event.quantity_delta)}</Badge>
                    </td>
                    <td>{event.source_type ? sourceLabels[event.source_type] || event.source_type : "-"}</td>
                    <td>{event.note || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}
